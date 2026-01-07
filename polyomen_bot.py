# polyomen_bot.py
import telebot
from telebot import types
import requests
import time
import threading
import re
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your bot token
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Channel ID
CHANNEL_ID = int(os.getenv('TELEGRAM_CHANNEL_ID', '-1003326210646'))  # @polyomen

bot = telebot.TeleBot(API_TOKEN)

# Store user subscriptions and watchlists
subscriptions = set()
watchlists = {}
alerts = {}
last_checked_markets = []

# Polymarket API
POLYMARKET_API = "https://gamma-api.polymarket.com"

def create_main_menu():
    """Create main menu keyboard"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🔥 Trending', '💰 Volume')
    markup.row('⭐ Watchlist', '🔔 Alerts')
    markup.row('🔮 Predict', '❓ Help')
    return markup

def get_markets():
    """Fetch active markets from Polymarket"""
    try:
        response = requests.get(f"{POLYMARKET_API}/markets?limit=100&closed=false")
        return response.json()
    except:
        return []

def get_market_by_slug(slug):
    """Get specific market details"""
    try:
        response = requests.get(f"{POLYMARKET_API}/markets/{slug}")
        return response.json()
    except:
        return None

def is_high_conviction(market):
    """Filter for high conviction markets only"""
    volume = float(market.get('volume', 0))
    liquidity = float(market.get('liquidity', 0))
    
    # Only post markets with significant activity
    return volume > 50000 or liquidity > 10000

def post_new_market(market):
    """Post high conviction markets to channel"""
    question = market.get('question', 'Unknown')
    condition_id = market.get('conditionId', 'N/A')
    volume = float(market.get('volume', 0))
    liquidity = float(market.get('liquidity', 0))
    end_date = market.get('endDate', 'TBD')
    
    # Format date better
    try:
        if end_date != 'TBD':
            date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            end_date = date_obj.strftime('%B %d, %Y at %H:%M UTC')
    except:
        pass
    
    # Build cleaner URL
    slug = market.get('slug', condition_id)
    market_url = f"https://polymarket.com/event/{slug}"
    
    message = f"""🔮 New Polymarket Event

{question}

🔗 Link: {market_url}

📊 Market stats:
Closes: {end_date}
Total Liquidity: ${liquidity:,.0f}
Total Volume: ${volume:,.0f}

📈 Current Odds: Loading..."""
    
    try:
        bot.send_message(CHANNEL_ID, message, disable_web_page_preview=False)
        print(f"Posted: {question[:50]}...")
    except Exception as e:
        print(f"Error posting to channel: {e}")

def check_new_markets():
    """Check for new high conviction markets"""
    global last_checked_markets
    
    while True:
        try:
            markets = get_markets()
            for market in markets:
                market_id = market.get('conditionId')
                
                # Only post high conviction + not posted before
                if market_id and market_id not in last_checked_markets and is_high_conviction(market):
                    post_new_market(market)
                    last_checked_markets.append(market_id)
                    time.sleep(5)  # Rate limit between posts
                    
                    # Keep list manageable
                    if len(last_checked_markets) > 100:
                        last_checked_markets = last_checked_markets[-50:]
            
            time.sleep(300)  # Check every 5 minutes instead of 1
        except Exception as e:
            print(f"Error checking markets: {e}")
            time.sleep(300)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    subscriptions.add(user_id)
    
    welcome = """🔮 Welcome to PolyOmen

Track and analyze Polymarket events.

🌐 Website: https://polyomen.app/
📢 Channel: @polyomen

You're subscribed to alerts! 🔔"""
    
    bot.reply_to(message, welcome, reply_markup=create_main_menu())

@bot.message_handler(commands=['trending'])
def trending(message):
    markets = get_markets()
    
    if not markets:
        bot.reply_to(message, "❌ Could not fetch markets")
        return
    
    # Sort by volume
    sorted_markets = sorted(markets, key=lambda x: float(x.get('volume', 0)), reverse=True)[:5]
    
    response = "🔥 Trending Markets:\n\n"
    for i, market in enumerate(sorted_markets, 1):
        question = market.get('question', 'Unknown')
        volume = float(market.get('volume', 0))
        response += f"{i}. {question}\n"
        response += f"   💰 Volume: ${volume:,.0f}\n\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['volume'])
def volume(message):
    markets = get_markets()
    
    if not markets:
        bot.reply_to(message, "❌ Could not fetch markets")
        return
    
    sorted_markets = sorted(markets, key=lambda x: float(x.get('volume', 0)), reverse=True)[:5]
    
    response = "💰 Highest Volume Markets:\n\n"
    for i, market in enumerate(sorted_markets, 1):
        question = market.get('question', 'Unknown')
        volume = float(market.get('volume', 0))
        condition_id = market.get('conditionId', 'N/A')
        response += f"{i}. {question}\n"
        response += f"   Volume: ${volume:,.0f}\n"
        response += f"   ID: {condition_id}\n\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['track'])
def track(message):
    user_id = message.chat.id
    args = message.text.split()[1:]
    
    if not args:
        bot.reply_to(message, "Usage: /track [market_id]")
        return
    
    slug = args[0]
    market = get_market_by_slug(slug)
    
    if not market:
        bot.reply_to(message, f"❌ Market '{slug}' not found")
        return
    
    if user_id not in watchlists:
        watchlists[user_id] = []
    
    if slug not in watchlists[user_id]:
        watchlists[user_id].append(slug)
        bot.reply_to(message, f"⭐ Added to watchlist: {market.get('question', slug)}")
    else:
        bot.reply_to(message, "Already in your watchlist")

@bot.message_handler(commands=['watchlist'])
def watchlist(message):
    user_id = message.chat.id
    
    if user_id not in watchlists or not watchlists[user_id]:
        bot.reply_to(message, "📋 Your watchlist is empty\n\nUse /track [id] to add markets")
        return
    
    response = "⭐ Your Watchlist:\n\n"
    for slug in watchlists[user_id]:
        market = get_market_by_slug(slug)
        if market:
            question = market.get('question', slug)
            response += f"• {question}\n  ID: {slug}\n\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['alert'])
def alert(message):
    user_id = message.chat.id
    args = message.text.split()[1:]
    
    if len(args) < 2:
        bot.reply_to(message, "Usage: /alert [market_id] [price]\nExample: /alert trump-wins 0.65")
        return
    
    slug = args[0]
    try:
        target_price = float(args[1])
    except:
        bot.reply_to(message, "❌ Invalid price format")
        return
    
    if user_id not in alerts:
        alerts[user_id] = []
    
    alerts[user_id].append({'slug': slug, 'price': target_price})
    bot.reply_to(message, f"🔔 Alert set: {slug} @ {target_price}")

@bot.message_handler(commands=['predict'])
def predict(message):
    """AI analysis from Polymarket URL"""
    text = message.text
    
    # Check if URL is in message
    if 'polymarket.com' not in text:
        bot.reply_to(message, "🔮 Send me a Polymarket link for AI analysis\n\nUsage:\n/predict https://polymarket.com/event/your-event-slug")
        return
    
    # Extract slug from URL
    try:
        # Pattern: https://polymarket.com/event/slug-here
        parts = text.split('polymarket.com/event/')
        if len(parts) < 2:
            bot.reply_to(message, "❌ Invalid Polymarket URL")
            return
            
        slug = parts[1].split()[0].strip()  # Get slug and remove any trailing text
        
        # Fetch market data by searching through markets
        try:
            response = requests.get(f"{POLYMARKET_API}/markets?limit=100&closed=false")
            markets = response.json()
            
            # Find market by slug
            market = None
            for m in markets:
                if m.get('slug') == slug:
                    market = m
                    break
            
            if not market:
                bot.reply_to(message, f"❌ Market not found. It may be older or not in the top 100 active markets.")
                return
        except:
            bot.reply_to(message, f"❌ Could not fetch market data")
            return
        
        question = market.get('question', 'Unknown')
        volume = float(market.get('volume', 0))
        liquidity = float(market.get('liquidity', 0))
        
        analysis = f"🔮 AI Market Analysis\n\n{question}\n\n"
        analysis += f"💰 Volume: ${volume:,.0f}\n"
        analysis += f"💧 Liquidity: ${liquidity:,.0f}\n\n"
        
        # Conviction level
        if volume > 100000:
            conviction = "High"
            analysis += "📊 Conviction: High\n\n"
            analysis += "Strong trader interest and market activity. Significant capital deployed.\n\n"
        elif volume > 10000:
            conviction = "Medium"
            analysis += "📊 Conviction: Medium\n\n"
            analysis += "Moderate activity. Developing market interest.\n\n"
        else:
            conviction = "Low"
            analysis += "📊 Conviction: Low\n\n"
            analysis += "Limited activity. Early-stage or niche market.\n\n"
        
        analysis += "⚠️ Not financial advice"
        
        bot.reply_to(message, analysis)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error analyzing market: {str(e)}")

@bot.message_handler(commands=['pause'])
def pause(message):
    user_id = message.chat.id
    if user_id in subscriptions:
        subscriptions.remove(user_id)
        bot.reply_to(message, "⏸️ Notifications paused\n\nUse /start to resume")
    else:
        bot.reply_to(message, "Already paused")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """📚 PolyOmen Commands:

📊 Market Info:
/trending - Hot markets now
/volume - High volume markets
/predict [id] - Market analysis
/deal [url] - Analyze event with AI

⭐ Watchlist:
/track [id] - Add to watchlist
/watchlist - Show watchlist

🔔 Alerts:
/alert [id] [price] - Set alert
/alerts - Show active alerts

⚙️ Settings:
/start - Subscribe to alerts
/pause - Pause notifications
/help - Show this message

🔗 Links:
🌐 https://polyomen.app/
📢 @polyomen"""
    
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['alerts'])
def show_alerts(message):
    user_id = message.chat.id
    
    if user_id not in alerts or not alerts[user_id]:
        bot.reply_to(message, "🔔 No active alerts\n\nUse /alert [id] [price] to set one")
        return
    
    response = "🔔 Your Alerts:\n\n"
    for alert in alerts[user_id]:
        response += f"• {alert['slug']} @ {alert['price']}\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['deal'])
def deal(message):
    """Analyze market from Polymarket URL"""
    text = message.text
    
    # Extract URL from message
    url_pattern = r'https://polymarket\.com/event/([a-zA-Z0-9\-]+)'
    match = re.search(url_pattern, text)
    
    if not match:
        bot.reply_to(message, "🔗 Send me a Polymarket link\n\nExample:\nhttps://polymarket.com/event/your-event-slug")
        return
    
    slug = match.group(1)
    
    # Get market data
    market = get_market_by_slug(slug)
    
    if not market:
        bot.reply_to(message, f"❌ Could not fetch market data")
        return
    
    question = market.get('question', 'Unknown')
    volume = float(market.get('volume', 0))
    liquidity = float(market.get('liquidity', 0))
    end_date = market.get('endDate', 'TBD')
    
    # Format response
    response = f"""🔮 {question}

🔗 Link: https://polymarket.com/event/{slug}

📊 Market stats:
Closes: {end_date}
Total Liquidity: ${liquidity:,.0f}
Total Volume: ${volume:,.0f}

📈 Current Odds:
- Long: Loading...
- Short: Loading...

🧠 Market Context:

Analysis based on current market data shows {"high" if volume > 100000 else "moderate" if volume > 10000 else "low"} conviction. Volume of ${volume:,.0f} indicates {"strong trader interest" if volume > 100000 else "developing interest" if volume > 10000 else "limited activity"}.

⚠️ This is not financial advice"""
    
    bot.reply_to(message, response)

# Add handlers for button presses
@bot.message_handler(func=lambda message: message.text == '🔥 Trending')
def button_trending(message):
    trending(message)

@bot.message_handler(func=lambda message: message.text == '💰 Volume')
def button_volume(message):
    volume(message)

@bot.message_handler(func=lambda message: message.text == '⭐ Watchlist')
def button_watchlist(message):
    watchlist(message)

@bot.message_handler(func=lambda message: message.text == '🔔 Alerts')
def button_alerts(message):
    show_alerts(message)

@bot.message_handler(func=lambda message: message.text == '❓ Help')
def button_help(message):
    help_command(message)

# Handle any other messages
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if not message.text.startswith('/'):
        bot.reply_to(message, "Send /help for available commands")

# Start market monitoring thread
print("🚀 Starting market monitor...")
market_thread = threading.Thread(target=check_new_markets, daemon=True)
market_thread.start()

# Start bot
print("🚀 PolyOmen Bot is running...")
bot.infinity_polling()
