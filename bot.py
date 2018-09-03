#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import telebot
import cherrypy

import config
from PSQL import DB

# Сервер ругается на SOCKS. Работает и без него
'''
telebot.apihelper.CONNECTION_TIMEOUT = 30
telebot.apihelper.proxy = {
    'http': 'socks5://telegram:telegram@erldo.tgproxy.me:443',
    'https': 'socks5://telegram:telegram@erldo.tgproxy.me:443'
}
'''

bot = telebot.TeleBot(config.token, threaded=False)

# Пока попробую вишневый сервер
    class WebhookServer(object):
        @cherrypy.expose
        def index(self):
            if 'content-length' in cherrypy.request.headers and \
               'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
                length = int(cherrypy.request.headers['content-length'])
                json_string = cherrypy.request.body.read(length).decode("utf-8")
                update = telebot.types.Update.de_json(json_string)
                bot.process_new_updates([update])
                return ''
            else:
                raise cherrypy.HTTPError(403)


@bot.message_handler(commands=["start"])
def start(message):
    db = DB()
    chat_id=message.chat.id
    username=message.from_user.username
    db.set_user_row(chat_id, username)
    db.close()
    keyboard = telebot.types.ReplyKeyboardMarkup( one_time_keyboard = True,resize_keyboard=True)
    iOS = telebot.types.KeyboardButton('iOS')
    Android = telebot.types.KeyboardButton('Android')
    keyboard.row(iOS,Android)
    bot.send_message(chat_id=message.chat.id,  text='Сіздің операциялық жүйеңізді таңдаңыз:', reply_markup= keyboard)


@bot.message_handler(func = lambda message: message.text == 'Android')
def Android(message):
    db = DB()
    db.set_download(chat_id=message.chat.id,OS='Android')
    db.close()
    bot.send_message(chat_id=message.chat.id,  text=config.instruct)
    bot.send_document(message.chat.id, 'BQADAgAD0gEAAks9AUjZitiVomJLaQI')
    bot.send_message(chat_id=message.chat.id,  text=config.warning)


@bot.message_handler(func = lambda message: message.text == 'iOS')
def iOS(message):
    db = DB()
    db.set_download(chat_id=message.chat.id,OS='iOS')
    db.close()
    bot.send_message(chat_id=message.chat.id,  text=config.instruct)
    bot.send_document(message.chat.id, 'BQADAgAD0wEAAks9AUinQbbWUaCHhQI')
    bot.send_message(chat_id=message.chat.id,  text=config.warning)


@bot.message_handler(content_types=["sticker", "pinned_message", "photo", "audio"])
def error_protection(message):
    pass


@bot.message_handler(func = lambda message: message.from_user.username == 'qz_gram' and message.text.startswith('***') )
def admin_dispatch(message):
    db = DB()
    ids = db.select_ids()
    db.close()
    for i in ids:
        print(i[0])
        bot.send_message(chat_id=i[0],  text=message.text[3:])


"""
Для изменения file_id
@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('C:/Users/Home/Desktop/Bots/Kazakh'):
        if file.split('.')[-1] == 'strings':
            f = open(''+file, 'rb')
            msg = bot.send_document(message.chat.id, f, None)
            # А теперь отправим вслед за файлом его file_id
            bot.send_message(message.chat.id, msg.document.file_id, reply_to_message_id=msg.message_id)
"""

if __name__ == '__main__':
    try:
        # Указываем настройки сервера CherryPy
        cherrypy.config.update({
        'server.socket_host': config.WEBHOOK_LISTEN,
        'server.socket_port': config.WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': config.WEBHOOK_SSL_CERT,
        'server.ssl_private_key': config.WEBHOOK_SSL_PRIV
        })
        bot.remove_webhook()
        bot.set_webhook(url=config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH,
                        certificate=open(config.WEBHOOK_SSL_CERT, 'r'))
        cherrypy.quickstart(WebhookServer(), config.WEBHOOK_URL_PATH, {'/': {}})
        #  bot.polling(none_stop=True)
    except Exception as e:
        f = open('logerr.txt', 'a')
        f.write(e)
        f.close()
