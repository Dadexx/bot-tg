import os
import requests
from keep_alive import keep_alive
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
keep_alive()

# Funzione per ottenere gli hashtag di TikTok
def get_tiktok_hashtags():
    """Estrae i primi 10 hashtag più popolari da Ritetag."""
    url = "https://ritetag.com/hashtag-search?green=0"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    hashtags = []
    for tag in soup.find_all('a', class_='tagstyleBig'):
        hashtag = tag.get('data-tag')
        if hashtag:
            hashtags.append(hashtag)

    return hashtags[:10]  # Restituisce solo i primi 10 hashtag

# Funzione per ottenere i trend di Google
def get_google_trends():
    """Ottiene i trend di Google nelle ultime 4 ore."""
    pytrends = TrendReq(hl='en')  # Cambia 'en' con la lingua desiderata
    trending_searches_df = pytrends.trending_searches(pn='united_states')  # Cambia se desideri altri Paesi

    return trending_searches_df.iloc[:10].values.tolist()

# Funzione di avvio del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invia un messaggio di benvenuto con emoji."""
    welcome_message = """
    👋 Ciao! Benvenuto nel bot per scoprire gli **hashtag più popolari su TikTok** e le **tendenze su Google**! 🌍

    📱 Usa il comando /trending per vedere gli hashtag più in voga e i trend globali!
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

# Funzione per inviare i trend di TikTok e Google
async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invia i trending topic da TikTok e Google Trends con emoji e formattazione."""
    tiktok_hashtags = get_tiktok_hashtags()
    google_trends_data = get_google_trends()

    response_text = "💎Hashtag più popolari su TikTok:💎\n\n"
    for hashtag in tiktok_hashtags:
        response_text += f"🟢 #{hashtag}\n"

    response_text += "\n🌍Tendenze su Google (ultime 4 ore):🌍\n\n"
    for trend in google_trends_data:
        response_text += f"🔥 {trend[0]}\n"  # `trend[0]` è il nome del trend

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

# Funzione principale per eseguire il bot
if __name__ == "__main__":
    # Estrai il token dalle variabili d'ambiente
    TOKEN = os.getenv('TELEGRAM_TOKEN')

    # Costruisci l'applicazione
    application = ApplicationBuilder().token(TOKEN).build()

    # Aggiungi i gestori per i comandi
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("trending", trending))

    # Esegui il bot
    application.run_polling()
