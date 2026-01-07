# 🔮 PolyOmen Bot

A Telegram bot that tracks and analyzes Polymarket prediction markets, automatically posting high-conviction markets to your channel.

## 🌟 Features

- **Auto-posting**: Monitors Polymarket API and posts high-conviction markets (>$50k volume or >$10k liquidity) to your Telegram channel
- **Market Tracking**: Track trending markets, high volume markets, and create personal watchlists
- **AI Analysis**: Get market analysis and conviction levels for any Polymarket event
- **Price Alerts**: Set alerts for specific markets at target prices
- **Interactive Menu**: Easy-to-use button interface for quick access to features

## 📋 Commands

### Market Info
- `/trending` - View hot markets right now
- `/volume` - See highest volume markets
- `/predict [url]` - Get AI analysis of a Polymarket event
- `/deal [url]` - Analyze market from Polymarket URL

### Watchlist
- `/track [id]` - Add market to your personal watchlist
- `/watchlist` - View your watchlist

### Alerts
- `/alert [id] [price]` - Set price alert for a market
- `/alerts` - Show your active alerts

### Settings
- `/start` - Subscribe to bot alerts
- `/pause` - Pause notifications
- `/help` - Show help message

## 🚀 Setup

### Prerequisites
- Python 3.7+
- Telegram Bot Token (from @BotFather)
- Telegram Channel

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd <repo-folder>
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your values:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
```

### Getting Your Bot Token

1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow the instructions
3. Copy the bot token provided
4. Paste it into `TELEGRAM_BOT_TOKEN` in your `.env` file

### Getting Your Channel ID

1. Create a public channel in Telegram
2. Add your bot as an administrator to the channel
3. Use the channel username (e.g., `-1003326210646`) or get the ID using a bot like @userinfobot
4. Paste it into `TELEGRAM_CHANNEL_ID` in your `.env` file

### Running the Bot

```bash
python polyomen_bot.py
```

The bot will:
- Start monitoring Polymarket for new high-conviction markets
- Post them to your channel every 5 minutes
- Respond to user commands in private chats

## 🔧 Configuration

### High-Conviction Filter

The bot filters markets based on:
- **Volume**: >$50,000
- **Liquidity**: >$10,000

You can adjust these thresholds in the `is_high_conviction()` function in `polyomen_bot.py`.

### Check Interval

Markets are checked every 5 minutes. Adjust this in the `check_new_markets()` function:
```python
time.sleep(300)  # 300 seconds = 5 minutes
```

## 📊 How It Works

1. **Market Monitoring**: Background thread checks Polymarket API every 5 minutes
2. **Filtering**: Only markets meeting high-conviction criteria are selected
3. **Auto-posting**: New markets are posted to your Telegram channel
4. **User Interaction**: Users can interact with the bot via commands for analysis and tracking

## 🔒 Security

- **Never commit `.env` file** - It contains your bot token
- The `.gitignore` file is configured to exclude sensitive files
- Always use environment variables for credentials

## 📢 Channel

Follow updates at: [@polyomen](https://t.me/polyomen)

## 📄 License

MIT License

## ⚠️ Disclaimer

This bot is for informational purposes only. Not financial advice. Use at your own risk.

---

Built for the Polymarket community 🔮
