import discord
from discord.ext import commands
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from datetime import datetime
import re

# Setup
TOKEN = os.environ['DISCORD_TOKEN']
SHEET_ID = os.environ['SHEET_ID']
GOOGLE_CREDS = json.loads(os.environ['GOOGLE_CREDENTIALS'])

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

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

@bot.event
async def on_ready():
    print(f'✓ Bot logged in as {bot.user}')
    print(f'✓ Listening for signups...')

@bot.event
async def on_message(message):
    # Don't log bot's own messages
    if message.author == bot.user:
        return
    
    # CHANGE THIS to your channel ID
    CHANNEL_ID = 1509236987247333446
    if message.channel.id != CHANNEL_ID:
        return
    
    try:
        # Parse email and URL from message
        email, url = parse_signup_message(message.content)
        
        # Only log if we found both email and URL (signup message)
        if email and url:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([timestamp, email, url])
            print(f'✓ Logged: {email} | {url}')
        
    except Exception as e:
        print(f'Error logging message: {e}')
    
    await bot.process_commands(message)

# Run bot
bot.run(TOKEN)
      
