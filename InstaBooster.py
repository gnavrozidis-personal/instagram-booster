import random
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        print("⏱️ Waiting 1.5 seconds after clicking followers link...")
        time.sleep(1.5)
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
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + 1000;', scroll_box)
            print("⏱️ Waiting 1 seconds after scroll...")
            time.sleep(1)
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
    print("⏱️ Waiting 2 seconds for profile page to load...")
    time.sleep(2)
    
    # Check if account is private first
    try:
        private = driver.find_element(By.XPATH, "//*[contains(text(), 'This Account is Private')]")
        follow_button = driver.find_element(By.XPATH, "//button[text()='Follow']")
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
                random_post = random.choice(valid_posts)
                print(f"Selected random post: {random_post.get_attribute('href')}")
                driver.get(random_post.get_attribute('href'))
                print("⏱️ Waiting 3 seconds for post to load...")
                time.sleep(3)
                try:
                    # Use the proven working selector from test
                    like_button = driver.find_element(By.XPATH, "//div[contains(@role, 'button') and contains(., 'Like')]")
                    # Use JavaScript click (same as successful test)
                    driver.execute_script("arguments[0].click();", like_button)
                    print(f'✓ Successfully liked a post of user: {user}')
                    
                    # Wait and verify like was successful
                    time.sleep(2)
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
        else:
            print('No posts found to like.')

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
        
        # Step 2: Get a random follower from the selected follower's followers (creates/uses {username}_followers.json)
        print(f"=== Step 2: Getting random follower from {follower1}'s followers ===")
        follower2 = get_random_follower(driver, user=follower1)
        if not follower2:
            print(f'No followers found for user {follower1}.')
            return
        
        print(f"Selected follower from {follower1}'s followers: {follower2}")
        
        # Step 3: Interact with the final selected user
        print(f"=== Step 3: Interacting with {follower2} ===")
        check_private_and_act(driver, follower2)
    except Exception as e:
        print(f'Error: {e}')
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
