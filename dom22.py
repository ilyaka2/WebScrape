import requests
import re
import datetime
import telebot
from bs4 import BeautifulSoup
from telegram import Update
from telegram.constants import ParseMode
from telebot import types
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = '7029054954:AAHunQqRc3WqaNY1epybJnb9zXWFZcZDdUw'# your BOT TOKEN need to change here to your BOT token!!!
PREDEFINED_URL = 'https://dom2-line.ru/svezhie-serii/'# for new episods
TARGET_CLASS = 'post-boxed'#Target class, using him for targeting this kind of class when parsering
NO_VIDEO_INDICATOR = "Эфир будет через несколько минут"# Message that indicates that there no video
TODAY_DATE = datetime.date.today()

bot = telebot.TeleBot(TOKEN)




# Function to fetch the HTML content of a website
def fetch_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
# Function to scrape the first three links from the articles with the specified class
def scrape_links(html_content, target_class, limit=6):
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = soup.find_all('article', class_=target_class, limit=limit)

    links = []
    for article in articles:
        link = article.find('a')
        if link and 'href' in link.attrs:
            links.append(link['href'])
        else:
            links.append("Link not found within the article.")
    print(links)
    return links
# Function to check the date of the link,returns the date of the link
def check_dates(links):
    formatted_date_today = TODAY_DATE.strftime("%d%m%Y")
    pattern = re.compile(r'\d{8}')
    dates = []
    for link in links:
        match = pattern.search(link)
        date = match.group()
        dates.append(date)
    return dates
# Function that count how many links without a video, returns the count of them
def not_valid_links_with_video(links):
    not_uploaded = 0
    for url in links:
        html_content = fetch_html(url)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            target_text = "Эфир будет через несколько минут"
            target_span = soup.find('span', style="font-family:arial, helvetica, sans-serif;", string=target_text)
            if target_span:
                not_uploaded += 1
    return not_uploaded
# Function to scrape the src attributes from the first three iframes
def scrape_iframe_sources(html_content, limit=6):
    soup = BeautifulSoup(html_content, 'html.parser')
    iframes = soup.find_all('iframe', limit=limit)

    sources = []
    for iframe in iframes:
        src = iframe.get('src')
        if src:
            # Ensure src attribute starts with a valid URL scheme
            if not src.startswith('http'):
                numbers = re.findall(r'\d+', src)
                numbers_str = ''.join(numbers)
                src = "https://ok.ru/video/" + numbers_str
            sources.append(src)

        else:
            sources.append("Source not found within the iframe.")
    print(sources)
    return sources
# Help function to reformat the date (helps for the response massage)
def format_date(date_str):
    day = date_str[:2]
    month = date_str[2:4]
    year = date_str[4:]
    return f"{day}.{month}.{year}"



# Telegram Bot start Command Handler
async def start(update: Update, context: CallbackContext):
    reply_keyboard = [["send!"]]

    await update.message.reply_text(
        "HI i your DOM2 bot, i will send you the videos:)",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
        ),
    )


#another Bot command hanfler, for future exdends
async def handle_hey_command(update: Update, context: CallbackContext):
    markup = types.InlineKeyboardMarkup(row_width=2)
    iron = types.InlineKeyboardButton('1 kilo of iron', callback_data='answer_iron')
    iron = types.InlineKeyboardButton('1 kilo of iron', callback_data='answer_iron')
    markup.add(iron)
    #bot.send_message(message.chat.id, 'what is lighter?', reply_markup=markup)

# Telegram Bot messages Handler, any massage
async def handle_message(update: Update, context: CallbackContext):
    html_content = fetch_html(PREDEFINED_URL)

    if html_content:
        links = scrape_links(html_content, TARGET_CLASS)
        #sources = scrape_iframe_sources(html_content)

        dates = check_dates(links)
        not_uploaded = not_valid_links_with_video(links)
        response = ""
        not_uploaded_response = ""
        dcount = 0




        for url in links:#enumerate(links):
            html_content = fetch_html(url)
            if html_content:
                sources = scrape_iframe_sources(html_content, 6)
                for src in sources:
                    #x = check_dates()
                    #dcount = not_uploaded

                    x = format_date(dates[dcount])
                    if not_uploaded != 0 :
                        not_uploaded -= 1
                        not_uploaded_response += (f"\n{x}\n{NO_VIDEO_INDICATOR}\n")

                    else:
                        response += (f"\n{x}\n{src}\n")
                    dcount += 1
                    print(dcount)
            else:
                print(f"Failed to retrieve content from {url}")
        if not_uploaded:# need to check here if there is a target span
            await update.message.reply_text(f"{not_uploaded_response}")
        #else
        await update.message.reply_text(f"{response}")

    else:
        await update.message.reply_text("Failed to retrieve the webpage.")


def main():
    # Replace 'TOKEN' with your actual bot token
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    #dp.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^hey$'), question))
    application.add_handler(CommandHandler("hey", handle_hey_command))
    application.run_polling()


if __name__ == '__main__':
    main()
