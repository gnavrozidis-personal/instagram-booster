import random
import time
import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def human_delay(min_delay=1.0, max_delay=3.0, action_type="general"):
    """
    Create human-like delays with randomization and normalization
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds  
        action_type: Type of action for context-aware delays
    """
    # Context-aware delay ranges
    delay_ranges = {
        "page_load": (2.0, 4.5),
        "click": (0.8, 2.2),
        "scroll": (1.2, 2.8),
        "api_call": (0.5, 1.5),
        "interaction": (1.5, 3.5),
        "navigation": (2.5, 4.0),
        "general": (min_delay, max_delay)
    }
    
    # Get appropriate delay range
    if action_type in delay_ranges:
        min_delay, max_delay = delay_ranges[action_type]
    
    # Generate random delay with slight bias toward middle values (more human-like)
    delay = random.uniform(min_delay, max_delay)
    
    # Add micro-variations (simulate human inconsistency)
    micro_variation = random.uniform(-0.1, 0.1)
    delay += micro_variation
    
    # Ensure minimum delay
    delay = max(delay, 0.5)
    
    print(f"⏱️ Human delay: {delay:.2f}s ({action_type})")
    time.sleep(delay)
    return delay

def detect_gender_free_api(profile_name):
    """
    Use free gender detection API with Greek context
    """
    try:
        # Extract first name (assumes format like "maria_k" or "maria k")
        first_name = profile_name.replace('_', ' ').split()[0]
        
        # Use free gender API with Greek context
        url = f"https://api.genderize.io/?name={first_name}&country_id=GR"
        response = requests.get(url)
        data = response.json()
        
        if data.get('gender'):
            probability = data.get('probability', 0)
            print(f"  Gender API: {first_name} -> {data['gender']} (confidence: {probability:.2f})")
            if probability > 0.6:  # Reasonable confidence for Greek names
                return data['gender']
            else:
                return "unknown"
        return "unknown"
        
    except Exception as e:
        print(f"Error with free API: {e}")
        return "unknown"

def filter_female_users(usernames, max_to_check=10):
    """
    Filter a list of usernames to find female users - stops at first female found
    """
    print(f"\n🔍 Checking gender - will stop at first female user found...")
    female_users = []
    checked = 0
    
    for username in usernames:
        if checked >= max_to_check:
            break
            
        print(f"\nChecking user {checked + 1}: {username}")
        gender = detect_gender_free_api(username)
        
        if gender == "female":
            female_users.append(username)
            print(f"  ✓ Female user found: {username}")
            print(f"  🎯 Stopping search - found first female user!")
            break  # Stop immediately when first female is found
        else:
            print(f"  ⚪ {username} -> {gender}")
            
        checked += 1
        # Be nice to the free API with randomized delays
        human_delay(action_type="api_call")
    
    print(f"\n📊 Results: Found {len(female_users)} female users out of {checked} checked")
    return female_users

def get_random_follower(driver, user=None, my_username=None):
    # Define cache file path - use specific naming for clarity
    if user:
        cache_file = f"{user}_followers.json"
    else:
        cache_file = "my_followers.json"
    
    # Check if cached followers exist
    if os.path.exists(cache_file):
        print(f"Found cached followers in {cache_file}")
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                valid_usernames = cached_data.get('followers', [])
                if valid_usernames:
                    username = random.choice(valid_usernames)
                    print(f"Selected follower from cache: {username}")
                    return username
        except Exception as e:
            print(f"Error reading cache file: {e}")
    
    print(f"No valid cache found for {user or 'your account'}. Fetching followers from Instagram...")
    
    if user:
        driver.get(f'https://www.instagram.com/{user}/')
    else:
        driver.get('https://www.instagram.com/')
        try:
            try:
                profile_element = None
                selectors = [
                    "//span[text()='Profile']",
                    "//a[contains(@href, '/') and .//span[text()='Profile']]",
                    "//span[contains(text(), 'Profile')]",
                    "//button[contains(text(), 'Profile')]",
                    "//div[contains(text(), 'Profile')]",
                    "//span[contains(@class, 'x1lliihq') and text()='Profile']",
                ]
                for selector in selectors:
                    try:
                        profile_element = driver.find_element(By.XPATH, selector)
                        print(f"Found Profile element using selector: {selector}")
                        break
                    except:
                        continue
                if profile_element:
                    profile_element.click()
                    current_url = driver.current_url
                    if current_url.count('/') >= 4:
                        my_username = current_url.strip('/').split('/')[-1]
                        print(f"Found username by clicking Profile: {my_username}")
                    else:
                        raise Exception("Profile click didn't lead to profile page")
                else:
                    raise Exception("Could not find Profile element with any selector")
            except Exception as e:
                print(f"Profile element method failed: {e}")
                my_username = None
                try:
                    profile_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/') and not(contains(@href, '/explore')) and not(contains(@href, '/direct')) and not(contains(@href, '/accounts'))]")
                    for link in profile_links:
                        href = link.get_attribute('href')
                        if href and href.count('/') >= 3:
                            username_candidate = href.strip('/').split('/')[-1]
                            if username_candidate and len(username_candidate) > 0 and username_candidate not in ['explore', 'direct', 'accounts', 'reels', 'stories']:
                                my_username = username_candidate
                                break
                except Exception:
                    pass
                if not my_username:
                    try:
                        profile_imgs = driver.find_elements(By.XPATH, "//img[@alt and contains(@alt, 'profile picture')]")
                        for img in profile_imgs:
                            parent_a = img.find_element(By.XPATH, './ancestor::a[1]')
                            href = parent_a.get_attribute('href')
                            if href and '/accounts/' not in href:
                                username_candidate = href.strip('/').split('/')[-1]
                                if username_candidate and len(username_candidate) > 0:
                                    my_username = username_candidate
                                    break
                    except Exception:
                        pass
                if not my_username:
                    raise Exception("Could not find username using any method")
                print(f"Found username: {my_username}")
        except Exception as e:
            print(f'Could not determine your username from the open session: {e}')
            return None
        if not driver.current_url.endswith(f'/{my_username}/'):
            driver.get(f'https://www.instagram.com/{my_username}/')
    try:
        followers_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//header//a[contains(@href, '/followers')]"))
        )
        driver.execute_script("arguments[0].click();", followers_link)
        print("⏱️ Waiting after clicking followers link...")
        human_delay(action_type="click")
    except Exception as e:
        print('Could not find or click the followers link.')
        return None
    try:
        followers_dialog = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]'))
        )
        scroll_box = None
        max_scroll_height = 0
        scroll_box_candidate = None
        print("Searching for scrollable container...")
        divs_with_overflow = followers_dialog.find_elements(By.XPATH, './/div[contains(@style, "overflow")]')
        for div in divs_with_overflow:
            try:
                sh = driver.execute_script('return arguments[0].scrollHeight', div)
                ch = driver.execute_script('return arguments[0].clientHeight', div)
                if sh > ch and sh > 100:
                    scroll_box = div
                    print(f"Found scrollable div with overflow style: scrollHeight={sh}, clientHeight={ch}")
                    break
            except Exception:
                continue
        if not scroll_box:
            containers = followers_dialog.find_elements(By.XPATH, './/div[.//a[contains(@href, "/")]]')
            for container in containers:
                try:
                    sh = driver.execute_script('return arguments[0].scrollHeight', div)
                    ch = driver.execute_script('return arguments[0].clientHeight', div)
                    if sh > ch and sh > max_scroll_height:
                        max_scroll_height = sh
                        scroll_box_candidate = container
                        print(f"Found potential container: scrollHeight={sh}, clientHeight={ch}")
                except Exception:
                    continue
        if not scroll_box:
            for div in followers_dialog.find_elements(By.XPATH, './/div'):
                try:
                    sh = driver.execute_script('return arguments[0].scrollHeight', div)
                    ch = driver.execute_script('return arguments[0].clientHeight', div)
                    if sh > ch and sh > max_scroll_height:
                        max_scroll_height = sh
                        scroll_box_candidate = div
                except Exception:
                    continue
            if scroll_box_candidate:
                scroll_box = scroll_box_candidate
                print(f"Using fallback scroll box: scrollHeight={max_scroll_height}")
        if not scroll_box:
            print('Scrollable box not found in followers dialog.')
            return None
    except Exception as e:
        print('Followers dialog did not appear or scrollable box not found.')
        return None
    try:
        WebDriverWait(driver, 15).until(
            lambda d: len(followers_dialog.find_elements(By.XPATH, ".//a[contains(@href, '/') and string-length(@href) > 2]")) > 0
        )
    except Exception:
        print('No followers loaded in the dialog. Dumping dialog HTML for debugging:')
        try:
            print(followers_dialog.get_attribute('outerHTML'))
        except Exception as e:
            print(f'Could not get dialog HTML: {e}')
        return None
    target_usernames = 200
    max_scroll_attempts = 80
    collected_usernames = set()
    import re
    no_new_users_count = 0
    for scroll_attempt in range(max_scroll_attempts):
        methods_tried = []
        scroll_worked = False
        successful_methods = []
        try:
            current_scroll = driver.execute_script('return arguments[0].scrollTop;', scroll_box)
            # Randomize scroll amount to appear more human
            scroll_amount = random.randint(800, 1200)
            driver.execute_script(f'arguments[0].scrollTop = arguments[0].scrollTop + {scroll_amount};', scroll_box)
            print("⏱️ Waiting after scroll...")
            human_delay(action_type="scroll")
            new_scroll = driver.execute_script('return arguments[0].scrollTop;', scroll_box)
            methods_tried.append("JS_SCROLL_BOX")
            if new_scroll > current_scroll:
                successful_methods.append("JS_SCROLL_BOX")
                scroll_worked = True
        except Exception:
            methods_tried.append("JS_SCROLL_BOX(failed)")
        all_links_now = followers_dialog.find_elements(By.XPATH, ".//a[contains(@href, '/') and string-length(@href) > 2]")
        current_usernames = set()
        for link_elem in all_links_now:
            href = link_elem.get_attribute('href')
            if href and '/liked_by/' in href:
                continue
            m = re.match(r'^https?://www.instagram.com/([A-Za-z0-9._]{1,30})/?$', href) or re.match(r'^/([A-Za-z0-9._]{1,30})/?$', href)
            username = m.group(1) if m else None
            if not username:
                continue
            current_usernames.add(username)
        new_users_this_round = len(current_usernames - collected_usernames)
        collected_usernames.update(current_usernames)
        if new_users_this_round == 0:
            no_new_users_count += 1
        else:
            no_new_users_count = 0
        scroll_status = "✓ Scrolled" if scroll_worked else "✗ No scroll"
        methods_status = f"Tried: [{', '.join(methods_tried)}] | Worked: [{', '.join(successful_methods)}]"
        print(f"[Scroll {scroll_attempt+1}] Unique usernames collected: {len(collected_usernames)} (+{new_users_this_round} new) - {methods_status} - {scroll_status}")
        if len(collected_usernames) >= target_usernames:
            print(f"Collected at least {target_usernames} usernames, stopping scroll.")
            break
        if no_new_users_count >= 8:
            print(f"No new users found for {no_new_users_count} attempts, likely reached end of followers list. Stopping scroll.")
            break
        if no_new_users_count > 5:
            print(f"No new users for {no_new_users_count} attempts, waiting longer...")
            human_delay(min_delay=2.0, max_delay=4.0, action_type="general")
    import re
    username_regex = re.compile(r'^[A-Za-z0-9._]{1,30}$')
    forbidden = set([
        'liked_by', 'following', 'followers', 'explore', 'direct', 'accounts', 'about', 'developer', 'privacy', 'terms', 'directory', 'topics', 'tags', 'reels', 'p', 'stories', 'igtv', 'tv', 'saved', 'notifications', 'settings', 'login', 'signup', 'email', 'phone', 'username', 'password', 'search', 'home', 'profile', 'edit', 'archive', 'activity', 'help', 'support', 'logout', 'discover', 'people', 'suggested', 'close_friends', 'live', 'shop', 'ads', 'business', 'creator', 'professional', 'meta', 'thread', 'threads', 'more'
    ])
    all_links = followers_dialog.find_elements(By.XPATH, ".//a[contains(@href, '/') and string-length(@href) > 2]")
    valid_usernames = []
    seen_usernames = set()
    for link_elem in all_links:
        href = link_elem.get_attribute('href')
        if href and '/liked_by/' in href:
            continue
        m = re.match(r'^https?://www.instagram.com/([A-Za-z0-9._]{1,30})/?$', href) or re.match(r'^/([A-Za-z0-9._]{1,30})/?$', href)
        username = m.group(1) if m else None
        if (username and username.lower() != 'liked_by' and 
            username_regex.match(username) and 
            username.lower() not in forbidden and 
            not username.startswith('.') and not username.endswith('.') and
            username not in seen_usernames):
            valid_usernames.append(username)
            seen_usernames.add(username)
    if not valid_usernames:
        print(f"No valid followers found. Found {len(all_links)} total links.")
        return None
    
    # Save followers to cache file
    cache_data = {
        'followers': valid_usernames,
        'timestamp': time.time(),
        'user': user or my_username
    }
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        print(f"Saved {len(valid_usernames)} followers to cache file: {cache_file}")
    except Exception as e:
        print(f"Error saving cache file: {e}")
    
    username = random.choice(valid_usernames)
    print(f"Selected follower: {username}")
    return username

def check_private_and_act(driver, user):
    driver.get(f'https://www.instagram.com/{user}/')
    print("⏱️ Waiting for profile page to load...")
    human_delay(action_type="page_load")
    
    # Check if account is private first
    try:
        private = driver.find_element(By.XPATH, "//*[contains(text(), 'This Account is Private')]")
        follow_button = driver.find_element(By.XPATH, "//button[text()='Follow']")
        # Add human-like delay before clicking follow
        human_delay(action_type="click")
        follow_button.click()
        print(f'Followed private user: {user}')
    except:
        # Account is public, look for posts
        posts = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')
        if posts:
            valid_posts = []
            for post in posts:
                href = post.get_attribute('href')
                if href and '/liked_by/' not in href and '/p/' in href:
                    valid_posts.append(post)
            if valid_posts:
                # Add small delay before selecting post (human-like browsing behavior)
                human_delay(min_delay=0.5, max_delay=1.5, action_type="general")
                random_post = random.choice(valid_posts)
                print(f"Selected random post: {random_post.get_attribute('href')}")
                driver.get(random_post.get_attribute('href'))
                print("⏱️ Waiting for post to load...")
                human_delay(action_type="page_load")
                try:
                    # Use the proven working selector from test
                    like_button = driver.find_element(By.XPATH, "//div[contains(@role, 'button') and contains(., 'Like')]")
                    # Add human-like delay before clicking like
                    human_delay(action_type="click")
                    # Use JavaScript click (same as successful test)
                    driver.execute_script("arguments[0].click();", like_button)
                    print(f'✓ Successfully liked a post of user: {user}')
                    
                    # Wait and verify like was successful
                    human_delay(action_type="interaction")
                    try:
                        unlike_elements = driver.find_elements(By.XPATH, "//*[@aria-label='Unlike']")
                        if unlike_elements:
                            print(f'✓ Confirmed: Post is now liked (found {len(unlike_elements)} Unlike elements)')
                        else:
                            print(f'? Like status unclear - but click was executed')
                    except:
                        print(f'? Could not verify like status')
                        
                except Exception as like_error:
                    print(f'Could not like the post with primary selector: {like_error}')
                    # Try alternative like button selectors with JavaScript click
                    alternative_selectors = [
                        "//*[@aria-label='Like']",
                        "//span[@aria-label='Like']", 
                        "//svg[@aria-label='Like']",
                        "//button[contains(@aria-label, 'Like')]"
                    ]
                    success = False
                    for selector in alternative_selectors:
                        try:
                            alt_like_button = driver.find_element(By.XPATH, selector)
                            driver.execute_script("arguments[0].click();", alt_like_button)
                            print(f'✓ Successfully liked post using alternative selector: {selector}')
                            success = True
                            break
                        except:
                            continue
                    if not success:
                        print('✗ Could not find any working like button selector.')
            else:
                print('No valid posts found to like.')
                # Try to find and click follow button as fallback
                try_follow_button(driver, user)
        else:
            print('No posts found to like.')
            # Try to find and click follow button as fallback
            try_follow_button(driver, user)

def try_follow_button(driver, user):
    """
    Try to find and click follow button when no posts are available
    """
    print(f"🔄 Looking for follow button for user: {user}")
    
    # Multiple selectors for follow button (based on successful test)
    follow_selectors = [
        # Primary selector that worked in test
        "//button[contains(@class, '_acan _acap _acas _aj1- _ap30')]//div[contains(text(), 'Follow')]",
        "//button[contains(@class, '_acan')]//div[contains(text(), 'Follow')]",
        
        # Alternative approaches
        "//button[.//div[contains(text(), 'Follow')] and contains(@class, '_acan')]",
        "//button[@type='button'][.//div[text()='Follow']]",
        "//button[@type='button'][contains(., 'Follow')]",
        
        # Class-based selectors
        "//div[contains(@class, '_ap3a') and text()='Follow']/ancestor::button",
        "//div[text()='Follow']/ancestor::button[1]",
        
        # More generic selectors
        "//button[text()='Follow']",
        "//button[contains(text(), 'Follow')]",
        "//button[contains(@aria-label, 'Follow')]",
        "//*[@role='button'][contains(., 'Follow')]",
        
        # Very broad fallback
        "//*[contains(text(), 'Follow') and (name()='button' or @role='button')]"
    ]
    
    follow_clicked = False
    
    for i, selector in enumerate(follow_selectors):
        try:
            print(f"  Trying follow selector {i+1}/{len(follow_selectors)}...")
            follow_buttons = driver.find_elements(By.XPATH, selector)
            
            if follow_buttons:
                for j, button in enumerate(follow_buttons):
                    try:
                        # Check if button is visible and clickable
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text.strip()
                            
                            # Verify it's actually a follow button
                            if 'Follow' in button_text:
                                print(f"  ✓ Valid follow button found: '{button_text}'")
                                
                                # Add human-like delay before clicking
                                human_delay(action_type="click")
                                
                                # Try JavaScript click first (more reliable)
                                driver.execute_script("arguments[0].click();", button)
                                print(f"✅ Successfully clicked follow button for user: {user}")
                                
                                # Wait to see if click was successful
                                human_delay(action_type="interaction")
                                
                                follow_clicked = True
                                break
                            else:
                                print(f"  ⚪ Button found but text is '{button_text}' (not Follow)")
                        else:
                            print(f"  ⚪ Button {j+1} not clickable (hidden or disabled)")
                            
                    except Exception as e:
                        print(f"  ❌ Error with button {j+1}: {str(e)[:50]}...")
                        continue
                
                if follow_clicked:
                    break
            else:
                print(f"  ❌ No elements found with selector {i+1}")
                
        except Exception as e:
            print(f"  ❌ Selector {i+1} failed: {str(e)[:50]}...")
            continue
    
    if not follow_clicked:
        print(f"❌ Could not find or click any follow button for user: {user}")
    
    return follow_clicked

def main():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        # Step 1: Get a random follower from YOUR followers (creates/uses my_followers.json)
        print("=== Step 1: Getting random follower from your followers ===")
        follower1 = get_random_follower(driver)
        if not follower1:
            print('No followers found.')
            return
        
        print(f"Selected follower from your followers: {follower1}")
        
        # Random delay between steps to appear more human
        human_delay(action_type="navigation")
        
        # Step 2: Get followers from the selected follower's account
        print(f"=== Step 2: Getting followers from {follower1}'s account ===")
        
        # First, get all followers from follower1
        cache_file = f"{follower1}_followers.json"
        followers_list = []
        
        if os.path.exists(cache_file):
            print(f"Found cached followers for {follower1}")
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    followers_list = cached_data.get('followers', [])
            except Exception as e:
                print(f"Error reading cache file: {e}")
        
        if not followers_list:
            print(f"No cached followers found. Fetching followers from {follower1}...")
            # Use the existing function to get followers
            get_random_follower(driver, user=follower1)
            # Try to load the newly created cache
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    followers_list = cached_data.get('followers', [])
        
        if not followers_list:
            print(f'No followers found for user {follower1}.')
            return
            
        print(f"Found {len(followers_list)} total followers for {follower1}")
        
        # Random delay before gender detection
        human_delay(action_type="general")
        
        # Step 3: Filter for female users
        print(f"=== Step 3: Finding female users among {follower1}'s followers ===")
        female_followers = filter_female_users(followers_list, max_to_check=40)
        
        if not female_followers:
            print("❌ No female users found in the checked followers.")
            print("🔄 Falling back to random follower selection...")
            follower2 = random.choice(followers_list)
        else:
            follower2 = female_followers[0]  # Only one female user since we stop at first
            print(f"✨ Selected female follower: {follower2}")
        
        # Random delay before final interaction
        human_delay(action_type="navigation")
        
        # Step 4: Interact with the final selected user
        print(f"=== Step 4: Interacting with {follower2} ===")
        check_private_and_act(driver, follower2)
        
    except Exception as e:
        print(f'Error: {e}')
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
