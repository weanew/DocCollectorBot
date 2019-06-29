from flask import Flask, request, abort
from flask_sslify import SSLify
import telebot
import logging
import time
import os
import subprocess

TOKEN = open('Token.txt', 'r').read().split('\n')[0]
bot = telebot.TeleBot(TOKEN)

telebot.logger.setLevel(logging.INFO)

app = Flask(__name__)
sslify = SSLify(app)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)

@bot.message_handler(content_types=['photo'])
def photo(message):
    fileID = message.photo[-1].file_id
    output = './bot/images/'
    file = bot.get_file(fileID)
    Path = file.file_path
    downloaded_file = bot.download_file(Path)
    print("File PATH = ", file.file_path)
    file_name = Path.split('/')[-1]
    with open(output + file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    PTH = output + file_name
    bash_command = 'python3 ./bot/scan.py --image ' + PTH
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    processed_PTH = './bot/scanned/' + file_name 
    upload_file = open(processed_PTH, 'rb')
    bot.send_photo(message.chat.id, upload_file)
    os.remove(PTH)
    os.remove(processed_PTH)

@app.route('/', methods=['POST'])
def getMessage():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        abort(403)


@app.route('/')
def webhook():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url='https://weanew.pythonanywhere.com/')
    return "!", 200


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port=int(os.environ.get('PORT', 5000)))