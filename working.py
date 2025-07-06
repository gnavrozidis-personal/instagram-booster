# & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_debug_profile"

import time
from selenium import webdriverclear
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_post_detection():
    """Test script to detect posts on a user's profile page"""
    
    # Connect to existing Chrome session
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("=== POST DETECTION TEST ===")
        print(f"Current URL: {driver.current_url}")
        
        # Wait a moment for page to load
        time.sleep(2)
        
        # Test multiple XPath selectors for posts
        selectors = [
            '//article//a[contains(@href, "/p/")]',  # Original selector
            '//a[contains(@href, "/p/")]',           # Broader selector
            '//div[contains(@class, "_aagu")]//a',   # Based on your example
            '//a[contains(@href, "/") and contains(@href, "/p/")]',  # More specific
            '//div//a[contains(@href, "/p/")]',      # Any div containing post links
        ]
        
        for i, selector in enumerate(selectors, 1):
            print(f"\n--- Test {i}: {selector} ---")
            try:
                posts = driver.find_elements(By.XPATH, selector)
                print(f"Found {len(posts)} elements")
                
                if posts:
                    valid_posts = []
                    for j, post in enumerate(posts[:5]):  # Check first 5 posts
                        try:
                            href = post.get_attribute('href')
                            if href:
                                print(f"  Post {j+1}: {href}")
                                if '/p/' in href and '/liked_by/' not in href:
                                    valid_posts.append(post)
                                    print(f"    ✓ Valid post")
                                else:
                                    print(f"    ✗ Invalid post (contains /liked_by/ or no /p/)")
                            else:
                                print(f"  Post {j+1}: No href attribute")
                        except Exception as e:
                            print(f"  Post {j+1}: Error getting href - {e}")
                    
                    print(f"Valid posts found: {len(valid_posts)}")
                    
                    if valid_posts:
                        print(f"✓ SUCCESS with selector: {selector}")
                        print(f"First valid post: {valid_posts[0].get_attribute('href')}")
                        
                        # Test clicking the first valid post
                        print("\nTesting click on first post...")
                        try:
                            first_post_url = valid_posts[0].get_attribute('href')
                            driver.get(first_post_url)
                            time.sleep(3)
                            
                            print(f"Navigated to: {driver.current_url}")
                            
                            # Test finding like button
                            like_selectors = [
                                "//span[@aria-label='Like']",
                                "//button[contains(@aria-label, 'Like')]",
                                "//div[contains(@role, 'button') and contains(., 'Like')]",
                                "//*[@aria-label='Like']",
                                "//svg[@aria-label='Like']",
                                "//button//span[contains(text(), 'Like')]"
                            ]
                            
                            print("\nTesting like button selectors...")
                            for k, like_selector in enumerate(like_selectors, 1):
                                try:
                                    like_buttons = driver.find_elements(By.XPATH, like_selector)
                                    print(f"  Like selector {k}: {like_selector} - Found {len(like_buttons)} elements")
                                    if like_buttons:
                                        print(f"    ✓ Like button found!")
                                        break
                                except Exception as e:
                                    print(f"  Like selector {k}: Error - {e}")
                            
                            break  # Exit the loop since we found working posts
                            
                        except Exception as e:
                            print(f"Error testing post click: {e}")
                else:
                    print("No posts found with this selector")
                    
            except Exception as e:
                print(f"Error with selector: {e}")
        
        # Additional debugging: Show page source snippet
        print("\n--- PAGE SOURCE ANALYSIS ---")
        try:
            # Look for common Instagram post patterns in page source
            page_source = driver.page_source
            patterns = ['/p/', '_aagu', 'article', 'post', 'href="/']
            
            for pattern in patterns:
                count = page_source.count(pattern)
                print(f"Pattern '{pattern}' appears {count} times in page source")
                
        except Exception as e:
            print(f"Error analyzing page source: {e}")
            
    except Exception as e:
        print(f"Main error: {e}")
        
    finally:
        print("\n=== TEST COMPLETE ===")
        print("Press Enter to close...")
        input()
        # Don't quit driver to keep Chrome open for inspection

if __name__ == '__main__':
    test_post_detection()
