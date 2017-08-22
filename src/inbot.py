# This example show how to write an inline mode telegramt bot use pyTelegramBotAPI.
import telebot
from telebot import TeleBot, types
import time
import sys
import logging
import re
from soundbot import *

API_TOKEN = ''

bot = telebot.TeleBot(API_TOKEN)
telebot.logger.setLevel(logging.DEBUG)


@bot.inline_handler(lambda query: len(query.query) > 3)
def query_card(inline_query):
    temp_list = []
    try:
        sound_dict = convert(inline_query.query)
        for key, sub_dict in sound_dict.items():
            for k, v in sub_dict.items():
                if k == 'GIF':
                    temp_list.append(types.InlineQueryResultArticle(id=key+k, 
                                                                    title=k, 
                                                                    input_message_content=types.InputTextMessageContent(sub_dict['Name']+"\'s ["+k+"] bit:\n"+v),
                                                                    reply_markup=None, 
                                                                    description=sub_dict['Name']+"\'s ["+k+"]", 
                                                                    thumb_url=sub_dict['Image'], 
                                                                    thumb_width=640, 
                                                                    thumb_height=640))
                if k not in ('Name', 'Image', 'GIF'):
                    temp_list.append(types.InlineQueryResultAudio(id=key+k, 
                                                                    title=sub_dict['Name']+"\'s ["+k+"]", 
                                                                    audio_url=v,
                                                                    reply_markup=None, 
                                                                    caption=sub_dict['Name']+"\'s ["+k+"] bit"))
        bot.answer_inline_query(inline_query.id, temp_list[0:49], cache_time=1)
    except Exception as e:
            print(e)

"""
# Safe inline card query function. Using InlineQueryResultArticle while I figure how to give cards format
@bot.inline_handler(lambda query: len(query.query) > 3)
def query_card(inline_query):
    temp_list = []
    try:
        sound_dict = scrape(inline_query.query)
        for key, sub_dict in sound_dict.items():
            for k, v in sub_dict.items():
                if k not in ('Name', 'Image'):
                    temp_list.append(types.InlineQueryResultArticle(id=key+k, 
                                                                    title=k, 
                                                                    input_message_content=types.InputTextMessageContent(sub_dict['Name']+"\'s ["+k+"] bit:\n"+v),
                                                                    reply_markup=None, 
                                                                    description=sub_dict['Name']+"\'s ["+k+"]", 
                                                                    thumb_url=sub_dict['Image'], 
                                                                    thumb_width=640, 
                                                                    thumb_height=640))
        bot.answer_inline_query(inline_query.id, temp_list[0:49], cache_time=1)
    except Exception as e:
            print(e)
"""

# Inline card query used when nothing is typed yet
gitgud = 'http://cloud-3.steamusercontent.com/ugc/547517466429744115/682DA0A373285668F4435E8C14EB171D58B0DCE0/'
@bot.inline_handler(lambda query: len(query.query) < 3)
def default_query(inline_query):
    try:
        r = types.InlineQueryResultArticle(id='1', 
        	                                title='Write a card name!', 
        	                                input_message_content=types.InputTextMessageContent(gitgud))
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
