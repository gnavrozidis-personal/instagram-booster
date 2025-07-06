import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_like_button_detection():
    """Test script to detect and click like button on Instagram post"""
    
    # Connect to existing Chrome session
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("=== LIKE BUTTON DETECTION TEST ===")
        print(f"Current URL: {driver.current_url}")
        
        # Wait a moment for page to load
        time.sleep(2)
        
        # Test multiple like button selectors
        like_selectors = [
            "//svg[@aria-label='Like']",                                    # Based on your example
            "//span//svg[@aria-label='Like']",                              # SVG inside span
            "//div//svg[@aria-label='Like']",                               # SVG inside div
            "//div[contains(@class, 'x6s0dn4')]//svg[@aria-label='Like']",  # Specific class from your example
            "//span[@aria-label='Like']",                                   # Original working selector
            "//div[contains(@role, 'button') and contains(., 'Like')]",     # Role-based selector
            "//div[contains(@role, 'button') and contains(., 'Like')]//svg", # SVG inside role button
            "//div[contains(@role, 'button') and contains(., 'Like')]//span", # Span inside role button
            "//button[contains(@aria-label, 'Like')]",                      # Button with aria-label
            "//*[@aria-label='Like']",                                      # Any element with Like aria-label
            "//svg[contains(@aria-label, 'Like')]",                         # Any SVG with Like aria-label
            "//div[contains(@class, 'x6s0dn4')]",                          # The outer div from your example
            "//div[contains(@class, 'x6s0dn4')]//span",                    # Span inside the outer div
            "//div[contains(@class, 'x6s0dn4')]//svg",                     # SVG inside the outer div
        ]
        
        print(f"\\nTesting {len(like_selectors)} like button selectors...")
        
        for i, selector in enumerate(like_selectors, 1):
            print(f"\\n--- Test {i}: {selector} ---")
            try:
                like_elements = driver.find_elements(By.XPATH, selector)
                print(f"Found {len(like_elements)} elements")
                
                if like_elements:
                    for j, element in enumerate(like_elements):
                        try:
                            # Get element information
                            tag_name = element.tag_name
                            aria_label = element.get_attribute('aria-label')
                            class_name = element.get_attribute('class')
                            parent_tag = element.find_element(By.XPATH, './..').tag_name
                            
                            print(f"  Element {j+1}:")
                            print(f"    Tag: {tag_name}")
                            print(f"    Aria-label: {aria_label}")
                            print(f"    Class: {class_name}")
                            print(f"    Parent tag: {parent_tag}")
                            print(f"    Is displayed: {element.is_displayed()}")
                            print(f"    Is enabled: {element.is_enabled()}")
                            
                            # Check if element is clickable
                            if element.is_displayed() and element.is_enabled():
                                print(f"    ✓ Element appears clickable")
                                
                                # Test click (but ask first)
                                print(f"\\n🎯 Found clickable like button with selector: {selector}")
                                response = input("Do you want to test clicking this like button? (y/n): ")
                                
                                if response.lower() == 'y':
                                    try:
                                        # Try clicking the element
                                        driver.execute_script("arguments[0].click();", element)
                                        print("✓ Successfully clicked like button using JavaScript!")
                                        print("Waiting 3 seconds to see result...")
                                        time.sleep(3)
                                        
                                        # Enhanced like state detection
                                        like_state_detected = False
                                        
                                        # Check for multiple indicators of like state change
                                        like_indicators = [
                                            "//svg[@aria-label='Unlike']",
                                            "//*[@aria-label='Unlike']", 
                                            "//svg[contains(@fill, 'red')]",
                                            "//svg[contains(@style, 'red')]",
                                            "//path[contains(@d, 'M34.6')]",  # Common filled heart path
                                        ]
                                        
                                        print("Checking for like state indicators...")
                                        for indicator in like_indicators:
                                            try:
                                                elements = driver.find_elements(By.XPATH, indicator)
                                                if elements:
                                                    print(f"  ✓ Found {len(elements)} elements with: {indicator}")
                                                    like_state_detected = True
                                                else:
                                                    print(f"  ✗ No elements found with: {indicator}")
                                            except:
                                                print(f"  ? Error checking: {indicator}")
                                        
                                        if like_state_detected:
                                            print("🎉 POST APPEARS TO BE LIKED!")
                                        else:
                                            print("❓ Like state unclear - maybe it was already liked or click didn't register")
                                            
                                            # Try alternative click methods
                                            print("Trying alternative click method...")
                                            try:
                                                element.click()
                                                print("✓ Tried regular click as backup")
                                                time.sleep(2)
                                            except Exception as alt_error:
                                                print(f"✗ Alternative click also failed: {alt_error}")
                                        
                                        return True  # Success, exit test
                                        
                                    except Exception as click_error:
                                        print(f"✗ Click failed: {click_error}")
                                        
                                        # Try clicking parent element
                                        try:
                                            print("Trying to click parent element...")
                                            parent = element.find_element(By.XPATH, './..')
                                            parent.click()
                                            print("✓ Clicked parent element")
                                            time.sleep(2)
                                        except Exception as parent_error:
                                            print(f"✗ Parent click failed: {parent_error}")
                                else:
                                    print("Skipped clicking")
                            else:
                                print(f"    ✗ Element not clickable")
                        except Exception as e:
                            print(f"  Element {j+1}: Error analyzing - {e}")
                else:
                    print("No elements found with this selector")
                    
            except Exception as e:
                print(f"Error with selector: {e}")
        
        # Additional analysis
        print("\\n--- ADDITIONAL ANALYSIS ---")
        try:
            # Check if we're on a post page
            if '/p/' in driver.current_url:
                print("✓ Currently on a post page")
            else:
                print("✗ Not on a post page - navigate to a post first")
                
            # Look for heart icons in page source
            page_source = driver.page_source
            heart_patterns = ['Like', 'Unlike', 'aria-label="Like"', 'svg', 'heart']
            
            print("\\nPattern analysis in page source:")
            for pattern in heart_patterns:
                count = page_source.count(pattern)
                print(f"  '{pattern}' appears {count} times")
                
        except Exception as e:
            print(f"Error in additional analysis: {e}")
            
    except Exception as e:
        print(f"Main error: {e}")
        
    finally:
        print("\\n=== TEST COMPLETE ===")
        print("Make sure you're on an Instagram post page before running this test.")
        print("Press Enter to close...")
        input()
        # Don't quit driver to keep Chrome open

if __name__ == '__main__':
    test_like_button_detection()
