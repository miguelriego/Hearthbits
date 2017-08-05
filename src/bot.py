from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
import logging

from soundbot import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.send_document(chat_id=update.message.chat_id, caption="Hearthbits wishes Andrew White a happy bday!!!", document="http://i.imgur.com/zqXA1WZ.gif")
    #bot.send_audio(chat_id=update.message.chat_id, caption="will it blend?", audio="http://media-Hearth.cursecdn.com/audio/card-sounds/sound/VO_BRM_019_Play_01.ogg")


def help(bot, update):
    update.message.reply_text('Help!')


def echo(bot, update):
    #update.message.reply_text(update.message.text)
    sound_dict = scrape(update.message.text)
    for k, v in sound_dict.items():
        if k != 'Name':
            bot.send_audio(chat_id=update.message.chat_id, caption=sound_dict['Name']+"\'s ["+k+"] bit", audio=v)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token='')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
