import telebot
from extensions import *


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def sterted(message: telebot.types.Message):
    text = 'Чтобы начать работу, введите команду боту в следующем формате:\n<Имя валюты> \
<в какую валюту перевести> \
<количество переводимой валюты>\
\nТак же вы можете увидеть список доступных валют написав команду: /values'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for k in keys.keys():
        text = '\n'.join((text, k))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def converter(message: telebot.types.Message):
    try:
        quote, base, amount = Examination.exam(message.text)
        text = Api.get_price(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду.\n {e}')
    else:
        bot.send_message(message.chat.id, text)


bot.polling()