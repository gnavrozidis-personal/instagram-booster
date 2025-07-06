# Instagram Automation Script

A Python script that automates Instagram interactions using Selenium WebDriver.

## Features

- Automatically selects random followers from your followers list
- Caches follower data for improved performance
- Handles both private and public accounts
- Likes random posts from public accounts
- Sends follow requests to private accounts

## Requirements

- Python 3.x
- Selenium WebDriver
- Chrome browser
- ChromeDriver (managed automatically via webdriver-manager)

## Installation

1. Install required packages:
```bash
pip install selenium webdriver-manager
```

2. Make sure Chrome browser is installed on your system

## Usage

1. Start Chrome with remote debugging:
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_dev"
```

2. Log into Instagram manually in the opened Chrome window

3. Run the script:
```bash
python insta_auto.py
```

## Important Notes

- This script is for educational purposes only
- Make sure to comply with Instagram's Terms of Service
- Use responsibly and avoid excessive automation that could get your account restricted
- The script creates cache files to store follower data for better performance

## Files

- `insta_auto.py` - Main automation script
- `test_*.py` - Test files for various components
- `working.py` - Additional working script

## Warning

Automating Instagram interactions may violate Instagram's Terms of Service. Use at your own risk.
