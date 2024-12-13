import os
import requests
from keep_alive import keep_alive
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton

keep_alive()

# Dizionario per memorizzare la lingua per ogni utente
user_languages = {}

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

# Funzione per inviare un messaggio di benvenuto in base alla lingua
async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    """Invia un messaggio di benvenuto con emoji in base alla lingua scelta."""
    
    messages = {
        'it': "👋 Ciao! Benvenuto nel bot per scoprire gli **hashtag più popolari su TikTok** e le **tendenze su Google**! 🌍\n\n📱 Usa il comando /trending per vedere gli hashtag più in voga e i trend globali!",
        'en': "👋 Hello! Welcome to the bot to discover the **most popular TikTok hashtags** and **Google trends**! 🌍\n\n📱 Use the /trending command to see trending hashtags and global trends!",
        'es': "👋 ¡Hola! ¡Bienvenido al bot para descubrir los **hashtags más populares de TikTok** y las **tendencias de Google**! 🌍\n\n📱 Usa el comando /trending para ver los hashtags más populares y las tendencias globales!"
    }

    # Invia il messaggio in base alla lingua
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.get(language, messages['en']))

# Funzione per gestire la selezione della lingua
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invia il messaggio di benvenuto con la selezione della lingua iniziale."""
    
    # Crea le opzioni di selezione della lingua
    keyboard = [
        [KeyboardButton("🇮🇹 Italiano"), KeyboardButton("🇬🇧 English"), KeyboardButton("🇪🇸 Español")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    # Chiedi all'utente di scegliere la lingua
    await update.message.reply_text("Ciao! Scegli la tua lingua / Choose your language / Elige tu idioma:", reply_markup=reply_markup)

# Funzione per gestire la risposta alla lingua
async def language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva la lingua scelta e invia il messaggio di benvenuto nella lingua scelta."""
    
    language_map = {
        '🇮🇹 Italiano': 'it',
        '🇬🇧 English': 'en',
        '🇪🇸 Español': 'es'
    }

    # Ottieni la lingua scelta dall'utente
    user_choice = update.message.text
    language = language_map.get(user_choice, 'en')  # Default a 'en' se la lingua non è riconosciuta

    # Salva la lingua per l'utente
    user_languages[update.effective_user.id] = language

    # Invia il messaggio di benvenuto nella lingua scelta
    await send_welcome_message(update, context, language)

# Funzione per inviare i trend di TikTok e Google
async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invia i trending topic da TikTok e Google Trends con emoji e formattazione."""
    
    user_id = update.effective_user.id
    language = user_languages.get(user_id, 'en')  # Usa la lingua dell'utente (default a 'en')

    tiktok_hashtags = get_tiktok_hashtags()
    google_trends_data = get_google_trends()

    messages = {
        'it': "💎Hashtag più popolari su TikTok:💎\n\n" + "\n".join([f"🟢 #{hashtag}" for hashtag in tiktok_hashtags]) + "\n\n🌍Tendenze su Google (ultime 4 ore):🌍\n\n" + "\n".join([f"🔥 {trend[0]}" for trend in google_trends_data]),
        'en': "💎Most popular TikTok hashtags:💎\n\n" + "\n".join([f"🟢 #{hashtag}" for hashtag in tiktok_hashtags]) + "\n\n🌍Google Trends (last 4 hours):🌍\n\n" + "\n".join([f"🔥 {trend[0]}" for trend in google_trends_data]),
        'es': "💎Hashtags más populares en TikTok:💎\n\n" + "\n".join([f"🟢 #{hashtag}" for hashtag in tiktok_hashtags]) + "\n\n🌍Tendencias en Google (últimas 4 horas):🌍\n\n" + "\n".join([f"🔥 {trend[0]}" for trend in google_trends_data])
    }

    # Invia il messaggio con i trend nella lingua selezionata
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.get(language, messages['en']))

# Funzione principale per eseguire il bot
if __name__ == "__main__":
    # Estrai il token dalle variabili d'ambiente
    TOKEN = os.getenv('TELEGRAM_TOKEN')

    # Costruisci l'applicazione
    application = ApplicationBuilder().token(TOKEN).build()

    # Aggiungi i gestori per i comandi
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("trending", trending))

    # Gestisci le risposte alla scelta della lingua
    application.add_handler(MessageHandler(filters.Regex("🇮🇹 Italiano|🇬🇧 English|🇪🇸 Español"), language_choice))

    # Esegui il bot
    application.run_polling()
