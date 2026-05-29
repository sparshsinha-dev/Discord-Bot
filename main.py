import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import re
import requests

# Setup credentials
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
SHEET_ID = os.environ['SHEET_ID']
GOOGLE_CREDS = json.loads(os.environ['GOOGLE_CREDENTIALS'])

# Google Sheets setup
scope = ['https://www.googleapis.com/auth/spreadsheets', 
         'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(GOOGLE_CREDS, scopes=scope)
gs = gspread.authorize(creds)
sheet = gs.open_by_key(SHEET_ID).sheet1

def parse_signup_message(content):
    """Extract Email and URL from signup message"""
    email = None
    url = None
    
    # Look for email pattern
    email_match = re.search(r'Email\s*[:\-]?\s*([^\s]+@[^\s]+)', content, re.IGNORECASE)
    if email_match:
        email = email_match.group(1)
    
    # Look for URL pattern
    url_match = re.search(r'URL\s*[:\-]?\s*(https?://[^\s]+)', content, re.IGNORECASE)
    if url_match:
        url = url_match.group(1)
    
    return email, url

def get_channel_messages(channel_id):
    """Fetch recent messages from Discord channel"""
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}"
    }
    
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=10"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            messages = response.json()
            return messages
        else:
            print(f"Error fetching messages: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def process_messages():
    """Process messages and log to Google Sheets"""
    CHANNEL_ID = 1234567890  # CHANGE THIS to your channel ID
    
    messages = get_channel_messages(CHANNEL_ID)
    
    for message in messages:
        content = message.get('content', '')
        author = message.get('author', {}).get('username', 'Unknown')
        
        # Only process messages with email and URL
        email, url = parse_signup_message(content)
        
        if email and url:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if already logged
            try:
                all_values = sheet.get_all_values()
                exists = False
                for row in all_values:
                    if len(row) >= 2 and row[1] == email and row[2] == url:
                        exists = True
                        break
                
                if not exists:
                    sheet.append_row([timestamp, email, url])
                    print(f'✓ Logged: {email} | {url}')
            except Exception as e:
                print(f'Error logging: {e}')

if __name__ == "__main__":
    print("✓ Bot starting...")
    print(f"✓ Monitoring channel for signups...")
    
    # Keep checking for messages every 30 seconds
    import time
    while True:
        try:
            process_messages()
            time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            print("\n✓ Bot stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)
