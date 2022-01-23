#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import requests
import telebot
import datetime
import config
import message_vars
import mongo_func
import pandas
import os
from requests.auth import HTTPBasicAuth

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    check_id = mongo_func.find_document(config.users_collection, {'telegram_id': message.chat.id}, True)
    if len(check_id) != 0:
        bot.register_next_step_handler(message, cogs_command)
    else:
        bot.send_message(message.from_user.id, message_vars.hello)

@bot.message_handler(commands=['help'])
def help_command(message):
 #   keyboard = telebot.types.InlineKeyboardMarkup()
 #   keyboard.add(
 #       telebot.types.InlineKeyboardButton('Написать в поддержку', url='mailto:support@market-place.me')
 #   )
 #   bot.send_message(message.chat.id, message_vars.help_var, reply_markup=keyboard)
    bot.send_message(message.chat.id, message_vars.help_var)

@bot.message_handler(commands=['cogs'])
def cogs_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Потрачено в этом месяце', callback_data='get-cogs-now')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Потрачено в прошлом месяце', callback_data='get-cogs-before')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Подробные траты в этом месяце', callback_data='get-cogs-now-detail')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Подробные траты в прошлом месяце', callback_data='get-cogs-before-detail')
    )
    bot.send_message(
        message.chat.id,
        'Выбери какие данные хочешь получить:',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: True)

def send_cogs_now(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if call.data == "get-cogs-now":
        bot.send_chat_action(call.message.chat.id, 'typing')
        query = mongo_func.find_document(config.users_collection, {'telegram_id': call.message.chat.id}, True)
        phone = {"phone": query[0]["phone"]}
        client = requests.get("http://service.tillypad.ru:8059/tillypad-api/market-place/get-client-by-phone",params=phone).json()
        f = open('../logs', 'a')
        f.write(str(datetime.datetime.now()) + ' процедура send_cogs_now. ответ Tillypad API ' + str(client) + ' \n')
        f.close()
        # Определение париода для передачи в параметрах в запрос https://mplace.space:20101/bi/query/cogs_client  -- начало
        today = datetime.date.today()
        datestart = str(today.strftime("%Y")) + str(today.strftime("%m")) + str('01')
        dateend = str(today.strftime("%Y")) + str(today.strftime("%m")) + str(today.strftime("%d"))
        # Определение париода для передачи в параметрах в запрос https://mplace.space:20101/bi/query/cogs_client  -- конец
        par = {'date_from' : datestart, 'date_to' : dateend, 'client_id' : client[0]["clnt_ID"]}
        f = open('../logs', 'a')
        f.write(str(datetime.datetime.now()) + ' процедура send_cogs_now. параметры для запроса с/с текущий месяц' + str(par) + ' \n')
        f.close()
        answer = requests.get('https://mplace.space:20101/bi/query/cogs_client', params=par, auth=HTTPBasicAuth('bi', 'bi')).json()
        f = open('../logs', 'a')
        f.write(
            str(datetime.datetime.now()) + ' процедура send_cogs_now. ответ запроса с/с текущий месяц ' + str(answer) + ' \n')
        f.close()
        if answer == 'None':
            bot.send_message(call.message.chat.id, 'Данных по операциям нет')
        else:
            bot.send_message(call.message.chat.id, 'Ты уже потратил приблизительно: ' + str(round(float(answer))) + ' руб.')
    elif call.data == "get-cogs-before":
        bot.send_chat_action(call.message.chat.id, 'typing')
        query = mongo_func.find_document(config.users_collection, {'telegram_id': call.message.chat.id}, True)
        phone = {"phone": query[0]["phone"]}
        client = requests.get("http://service.tillypad.ru:8059/tillypad-api/market-place/get-client-by-phone", params=phone).json()
        f = open('../logs', 'a')
        f.write(str(datetime.datetime.now()) + ' процедура send_cogs_now. ответ Tillypad API ' + str(client) + ' \n')
        f.close()
        #Определение париода для передачи в параметрах в запрос https://mplace.space:20101/bi/query/cogs_client  -- начало
        today = datetime.date.today()
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)
        datestart = str(lastMonth.strftime("%Y")) + str(lastMonth.strftime("%m")) + str('01')
        dateend = str(lastMonth.strftime("%Y")) + str(lastMonth.strftime("%m")) + str(lastMonth.strftime("%d"))
        #Определение париода для передачи в параметрах в запрос https://mplace.space:20101/bi/query/cogs_client  -- конец
        par = {'date_from': datestart, 'date_to': dateend, 'client_id': client[0]["clnt_ID"]}
        f = open('../logs', 'a')
        f.write(str(datetime.datetime.now()) + ' процедура send_cogs_now. параметры для запроса с/с текущий месяц' + str(par) + ' \n')
        f.close()
        answer = requests.get('https://mplace.space:20101/bi/query/cogs_client', params=par, auth=HTTPBasicAuth('bi', 'bi')).json()
        f = open('../logs', 'a')
        f.write(
            str(datetime.datetime.now()) + ' процедура send_cogs_now. ответ запроса с/с текущий месяц ' + str(answer) + ' \n')
        f.close()
        if answer == 'None':
            bot.send_message(call.message.chat.id, 'Данных по операциям нет')
        else:
            bot.send_message(call.message.chat.id, 'Ты уже потратил приблизительно: ' + str(round(float(answer))) + ' руб.')
    elif call.data == "get-cogs-now-detail":
        bot.send_chat_action(call.message.chat.id, 'typing')
        query = mongo_func.find_document(config.users_collection, {'telegram_id': call.message.chat.id}, True)
        phone = {"phone": query[0]["phone"]}
        client = requests.get("http://service.tillypad.ru:8059/tillypad-api/market-place/get-client-by-phone", params=phone).json()
        # Определение париода для передачи в параметрах в запрос https://mplace.space:20101/bi/query/cogs_client  -- начало
        today = datetime.date.today()
        datestart = str(today.strftime("%Y")) + str(today.strftime("%m")) + str('01')
        dateend = str(today.strftime("%Y")) + str(today.strftime("%m")) + str(today.strftime("%d"))
        # Определение париода для передачи в параметрах в запрос https://mplace.space:20101/bi/query/cogs_client  -- конец
        par = {'date_from': datestart, 'date_to': dateend, 'client_id': client[0]["clnt_ID"]}
        answer = requests.get('https://mplace.space:20101/bi/query/cogs_client_detail', params=par, auth=HTTPBasicAuth('bi', 'bi')).json()
        if answer == 'None' or answer == None:
            bot.send_message(call.message.chat.id, 'Данных по операциям нет')
        else:
            os.chdir("./tempfiles")
            filejson = str(call.message.chat.id) + '.json'
            filecsv  = str(call.message.chat.id) + '_current_month' + '.csv'
            with open(filejson, 'w') as outfile:
                json.dump(answer['data'], outfile)
            df = pandas.read_json(filejson)
            f = open(filecsv, 'w')
            f.write('Ресторан; Дата; ID блюда; Блюдо; Кол-во; Себестоимость \n')
            f.close()
            df.to_csv(filecsv, sep=";", header=False, encoding="ansi", index=None, mode="a", decimal=",")
            f = open(filecsv, "rb")
            bot.send_document(call.message.chat.id, f)
            os.remove(filejson)
            os.chdir("../")
    else:
        bot.send_chat_action(call.message.chat.id, 'typing')
        query = mongo_func.find_document(config.users_collection, {'telegram_id': call.message.chat.id}, True)
        phone = {"phone": query[0]["phone"]}
        client = requests.get("http://service.tillypad.ru:8059/tillypad-api/market-place/get-client-by-phone", params=phone).json()
        # Определение париода для передачи в параметрах в запрос https://mplace.space:20101/bi/query/cogs_client  -- начало
        today = datetime.date.today()
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)
        datestart = str(lastMonth.strftime("%Y")) + str(lastMonth.strftime("%m")) + str('01')
        dateend = str(lastMonth.strftime("%Y")) + str(lastMonth.strftime("%m")) + str(lastMonth.strftime("%d"))
        # Определение париода для передачи в параметрах в запрос https://mplace.space:20101/bi/query/cogs_client  -- конец
        par = {'date_from': datestart, 'date_to': dateend, 'client_id': client[0]["clnt_ID"]}
        answer = requests.get('https://mplace.space:20101/bi/query/cogs_client_detail', params=par, auth=HTTPBasicAuth('bi', 'bi')).json()
        if answer == 'None' or answer == None:
            bot.send_message(call.message.chat.id, 'Данных по операциям нет')
        else:
            os.chdir("./tempfiles")
            filejson = str(call.message.chat.id) + '.json'
            filecsv  = str(call.message.chat.id) + '_last_month' + '.csv'
            with open(filejson, 'w') as outfile:
                json.dump(answer['data'], outfile)
            df = pandas.read_json(filejson)
            f = open(filecsv, 'w')
            f.write('Ресторан; Дата; ID блюда; Блюдо; Кол-во; Себестоимость \n')
            f.close()
            df.to_csv(filecsv, sep=";", header=False, encoding="ansi", index=None, mode="a", decimal=",")
            f = open(filecsv, "rb")
            bot.send_document(call.message.chat.id, f)
            os.remove(filejson)
            os.chdir("../")
    keyboard.row(
        telebot.types.InlineKeyboardButton('Потрачено в этом месяце', callback_data='get-cogs-now')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Потрачено в прошлом месяце', callback_data='get-cogs-before')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Подробные траты в этом месяце', callback_data='get-cogs-now-detail')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Подробные траты в прошлом месяце', callback_data='get-cogs-before-detail')
    )
    bot.send_message(
        call.message.chat.id,
        'Выбери за какой месяц показать себестоиомсть твох заказов:',
        reply_markup=keyboard
    )

@bot.message_handler(content_types=['text'])
def reg(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, "Укажи свой номер телефона в формате +79999999999")
        if message.text == '/cogs':
            bot.register_next_step_handler(message, cogs_command)
            return
        else:
            bot.register_next_step_handler(message, reg_phone)
    else:
        bot.send_message(message.from_user.id, 'Сначала надо зарегистрироваться. Напиши /reg или /cogs если уже зарегистрирован')

def reg_phone(message):
    phone = {"phone": message.text}
    if len(message.text) == 12:
        f = open('../logs', 'a')
        f.write(str(datetime.datetime.now()) + ' пользователь tg_id ' + str(message.chat.id) + ' отправил сообщение ' + message.text + '\n')
        f.close()
        bot.send_message(message.from_user.id, 'Ты указал номер телефона ' + message.text + " ищу твой номер в Tillypad")
        bot.send_chat_action(message.chat.id, 'typing')                                 # отправляем иммитацую как буд-то бот печатает, пока выполянется запрос
        check_id = mongo_func.find_document(config.users_collection, {'telegram_id': message.chat.id}, True)
        if len(check_id) == 0:
            client = requests.get("http://service.tillypad.ru:8059/tillypad-api/market-place/get-client-by-phone",params=phone).json()
            if len(client) == 0:

                f = open('../logs', 'a')
                f.write(str(datetime.datetime.now()) + ' ответ Tillypad API ' + str(client) + ' Сотрудник не найден \n')
                f.close()
                bot.send_message(message.from_user.id, 'Твой номер телефона ' + message.text + 'не найден в БД Marketplace, проверь не ошибся ли в нём. \n'
                                                                                               'Если ошибся повтори ввод номера, \n'
                                                                                               'если все верно, а клиент все равно не найден, то напиши в поддержку')
                bot.register_next_step_handler(message, reg_phone)
            else:
                f = open('../logs', 'a')
                f.write(str(datetime.datetime.now()) + ' сотрудник найден ' + str(client) + '\n')
                f.close()
                new_user = {
                    "telegram_id": message.chat.id,
                    "phone": message.text
                }
                res = mongo_func.insert_document(config.users_collection, new_user)
                f = open('../logs', 'a')
                f.write(str(datetime.datetime.now()) + ' результат добавления в БД ' + str(res) + '\n')
                f.close()
                bot.send_message(message.from_user.id, 'Ты успешно зарегистирован(а). Твой ID в Tillypad: ' + client[0]["clnt_ID"])
                bot.send_message(message.from_user.id, 'Судя по Tillypad тебя зовут: ' + client[0]["clnt_Name"])
                bot.send_message(message.from_user.id, 'Для получения информации по с/с питания набери команду /cogs')
        else:
            bot.send_message(message.from_user.id, 'Ты уже зарегистрирован, можешь получать информацию о себестоиомсти, напиши команду /cogs')
            mongo_func.update_document(config.users_collection, {'telegram_id': message.chat.id},{'phone' : message.text})
    else:
        bot.send_message(message.from_user.id, 'Похоже ты сделал ошибку в номере, вот что ты указал ' + message.text + ' Напоминаю формат должен быть +79999999999, попробуй снова')
        bot.register_next_step_handler(message, reg_phone)


bot.polling(none_stop=True, interval=0)
