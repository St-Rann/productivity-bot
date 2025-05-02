# Productivity Coach Telegram Bot

A Telegram bot to help you stay productive!  
✅ Task management  
✅ GPT-powered coaching  
✅ Inline buttons  
✅ Usage tracking  
✅ Donation support

## Setup

1. Clone this repo.
2. Add `.env` file with:
   ```
   BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run locally:
   ```
   python main.py
   ```
5. (Optional) Use Docker:
   ```
   docker build -t productivity-bot .
   docker run -d -p 8000:8000 productivity-bot
   ```

## Deploy

- **Railway:** Connect GitHub, set env vars, deploy.
- **Heroku:** Use `Procfile`, push to Heroku.

## Donate

Support the project → https://buymeacoffee.com/yourpage
