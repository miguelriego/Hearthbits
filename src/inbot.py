# This example show how to write an inline mode telegramt bot use pyTelegramBotAPI.
import telebot
import time
import sys
import logging
import re
from telebot import *
from soundbot import *

API_TOKEN = '428829269:AAHku3MWFL02S2J5Ira5dWHj-koIbwBCkHg'

bot = telebot.TeleBot(API_TOKEN)
telebot.logger.setLevel(logging.DEBUG)


# WORKS: Builds inline card query function. Using InlineQueryResultArticle while I figure how to give cards format
@bot.inline_handler(lambda query: len(query.query) > 0)
def query_card(inline_query):
    temp_list = []
    try:
        sound_dict = scrape(inline_query.query)
        for k, v in sound_dict.items():
            if k != 'Name':
                print(k,v)
                temp_list.append(types.InlineQueryResultArticle(k, k, types.InputTextMessageContent(sound_dict['Name']+"\'s ["+k+"] bit:\n"+v), None, 'http://telegram.org', True,  'Subtitle 1', 'https://telegram.org/img/t_logo.png',640, 640))
                #temp_list.append(types.InlineQueryResultVoice(id=k, voice_url=v, title="^ "+sound_dict['Name']+"\'s ["+k+"] bit:\n"+v, caption=sound_dict['Name']+"\'s ["+k+"] bit"))
        bot.answer_inline_query(inline_query.id, temp_list, cache_time=1)
    except Exception as e:
            print(e)


@bot.inline_handler(lambda query: len(query.query) is 0)
def default_query(inline_query):
    try:
        r = types.InlineQueryResultArticle('1', 'Write a full card name!', types.InputTextMessageContent('default'))
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)


def main_loop():
    bot.polling(True)
    while 1:
        time.sleep(3)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)