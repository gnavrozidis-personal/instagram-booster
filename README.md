# InstaBooster - Instagram Automation Script

An advanced Instagram automation script that intelligently finds and interacts with female users using AI-powered gender detection.

## 🎯 What It Does

1. **Gets a random follower** from your Instagram followers
2. **Fetches all followers** from that selected follower's account
3. **Uses AI gender detection** to identify female users (with Greek context support)
4. **Stops at the first female user** found for efficiency
5. **Interacts intelligently** - likes posts from public accounts or follows private accounts

## ✨ Key Features

- **Smart Gender Detection**: Uses Genderize.io API with Greek context for accurate gender identification
- **Efficient Searching**: Stops immediately when first female user is found
- **Intelligent Caching**: Saves follower data to avoid repeated Instagram scraping
- **Dual Action Mode**: Handles both public (likes posts) and private accounts (sends follow requests)
- **Respectful API Usage**: Built-in delays to respect rate limits
- **Clean Output**: Clear progress indicators and status messages

## 📋 Requirements

- Python 3.7+
- Chrome browser
- Active Instagram account
- Internet connection for API calls

## 🚀 Installation

1. **Install required Python packages:**
```bash
pip install selenium webdriver-manager requests
```

2. **Verify Chrome is installed** on your system

## 🔧 Setup Instructions

### Step 1: Start Chrome with Remote Debugging
Run this command in your terminal/command prompt:

**Windows:**
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_dev"
```

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev"
```

**Linux:**
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev"
```

### Step 2: Login to Instagram
1. A new Chrome window will open
2. Navigate to Instagram.com
3. Log in with your Instagram credentials
4. **Keep this window open** while running the script

### Step 3: Run the Script
```bash
python InstaBooster.py
```

## 📊 How It Works

```
Your Followers → Random Selection → Get Their Followers → Gender Check → Female Found → Interact
```

### Detailed Workflow:
1. **Follower Selection**: Randomly picks one of your followers
2. **Data Gathering**: Collects all followers from that user's account
3. **Gender Analysis**: Uses Genderize.io API to detect gender of usernames
4. **Efficient Filtering**: Stops checking as soon as first female user is found
5. **Smart Interaction**: 
   - Public accounts: Likes a random post
   - Private accounts: Sends follow request

## 📁 Cache Files

The script creates JSON cache files to improve performance:
- `my_followers.json` - Your followers (cached for reuse)
- `{username}_followers.json` - Cached followers for each user checked

## ⚙️ Configuration

### Gender Detection Settings:
- **Confidence Threshold**: 0.6 (60% confidence required)
- **Context**: Greek names support (`country_id=GR`)
- **API Rate Limit**: 0.5 second delay between calls

### Follower Collection Settings:
- **Target Collection**: 200 usernames per user
- **Max Scroll Attempts**: 80 attempts
- **Scroll Delay**: 1 second between scrolls

## 🔍 Troubleshooting

### Common Issues:

**"No followers found"**
- Ensure you're logged into Instagram
- Check if the selected user has public followers
- Verify your internet connection

**"Gender API Error"**
- Check your internet connection
- Genderize.io might be temporarily unavailable
- Script will continue with random selection as fallback

**"Could not find like button"**
- Instagram may have changed their interface
- Script includes multiple backup selectors
- Try running again later

**Chrome Connection Issues**
- Ensure Chrome is running with remote debugging
- Check that port 9222 is not blocked
- Restart Chrome with the debugging command

## 🚨 Important Warnings

- **Educational Purpose Only**: This script is for learning automation concepts
- **Instagram ToS**: Automated actions may violate Instagram's Terms of Service
- **Account Safety**: Use at your own risk - could result in account restrictions
- **Rate Limits**: Script includes delays but Instagram may still detect automation
- **Ethical Use**: Respect other users' privacy and consent

## 📊 API Usage

The script uses the free tier of Genderize.io:
- **Free Limit**: 1000 requests per day
- **No API Key Required**: Works out of the box
- **Greek Context**: Optimized for Greek names with `country_id=GR`

## 🔧 Advanced Configuration

To modify behavior, edit these settings in `InstaBooster.py`:

```python
# Maximum users to check for gender (default: 40)
female_followers = filter_female_users(followers_list, max_to_check=40)

# Confidence threshold for gender detection (default: 0.6)
if probability > 0.6:  # Adjust this value

# API delay between requests (default: 0.5 seconds)
time.sleep(0.5)  # Increase for more conservative rate limiting
```

## 📈 Performance Tips

- **Use Cached Data**: Let the script build cache files for frequently checked users
- **Optimal Timing**: Run during off-peak hours for better Instagram performance
- **Batch Processing**: Allow the script to complete full cycles for better efficiency
- **Monitor Output**: Watch the console for progress and any issues

## 🤝 Contributing

This is an educational project. Feel free to fork and modify for learning purposes.

## 📄 License

This project is for educational purposes only. Use responsibly and in compliance with all applicable terms of service and laws.
