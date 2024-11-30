import asyncio
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters import Text
from main import dp, bot
import mysql.connector
from keyboards import *
import random
import math
import traceback
from freekassa_ru import FreekassaError, FreekassaAuthError
import hashlib
from urllib.parse import urlencode
import aiofiles
import json
import requests
import datetime
import aiohttp
from pycbrf.toolbox import ExchangeRates
from vkbottle import CtxStorage
from dotenv import load_dotenv
from freekassa_ru import Freekassa
import csv
import aiofiles
from aiocsv import AsyncReader, AsyncDictReader, AsyncWriter, AsyncDictWriter
import os

load_dotenv()

iddebug, idnews, idfree, token, api_subgraph, lolzlink, support = os.getenv('iddebug'), os.getenv('idnews'), os.getenv('iddebug'), os.getenv('token'), os.getenv('subgraph_keys'), os.getenv('lolzlink'), os.getenv('support')

ctx = CtxStorage()

defaultheaders = {
    "accept": "application/json",
    'User-Agent': 'AppleCoreMedia/1.0.0.20L563 (Apple TV; U; CPU OS 16_5 like Mac OS X; en_ca)'
    }
        
rates = ExchangeRates(datetime.datetime.now().strftime("%Y-%m-%d"))
        
async def async_http_get(url, headers):
    
            async with aiohttp.ClientSession() as session:
                
                async with session.get(url=url, headers=headers) as response:
                    
                    try:

                        return await read_stream_json(response)
                    
                    except:
                        
                        print(response.status)
    
async def async_http_post(url, headers, query):
        
        async with aiohttp.ClientSession() as session:
            
            async with session.post(url, json=query) as response:
                
                return await read_stream_json(response)
        
async def read_stream_json(stream):
        
        data = await stream.read()
        
        json_data = json.loads(data.decode())
        
        return json_data
        
class BuyBill(StatesGroup):
        count = State()
        days = State()
        
class LiveParser(StatesGroup):
        count = State()
        
class MaxBalance(StatesGroup):
        maxbalance = State()    
        
class Spam(StatesGroup):
    message = State()
    
class Test(StatesGroup):
    lolz = State()

async def cryptobillcreate(amount):
    try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_settings')
                                parser_settings = cursor.fetchone()
    finally:            
        connection.close()
        api_key, id_shop = parser_settings[11], parser_settings[12]
        headerscrypto = {
                                "accept": "application/json",
                                'User-Agent': 'AppleCoreMedia/1.0.0.20L563 (Apple TV; U; CPU OS 16_5 like Mac OS X; en_ca)',
                                'Authorization': 'Token ' + api_key.rstrip()
        }
    
    a = requests.post(    url='https://api.cryptocloud.plus/v1/invoice/create', headers=headerscrypto, data={
                'shop_id': id_shop,
                'amount': amount,
                'currency': 'USD'}).json()
    
    print(a)
    
    link, payid = a['pay_url'], a['invoice_id']
    
    return link, payid

async def checkcryptopay(id_pay):
    try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_settings')
                                parser_settings = cursor.fetchone()
    finally:            
        connection.close()
                            
        api_key, id_shop = parser_settings[11], parser_settings[12]
        
        headerscrypto = {
                                "accept": "application/json",
                                'User-Agent': 'AppleCoreMedia/1.0.0.20L563 (Apple TV; U; CPU OS 16_5 like Mac OS X; en_ca)',
                                'Authorization': 'Token ' + api_key.rstrip()
        }
        
        calldata = requests.get(url='https://api.cryptocloud.plus/v1/invoice/info', headers=headerscrypto, params={'uuid': id_pay})
        
        calldata = calldata.json()
        
        print(calldata)
        
        if calldata['status_invoice'] == 'paid':
            return 'ok'
        else:
            return 'fail'
        
async def createbillfiat(amount, chatid):
    
    try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_settings')
                                parser_settings = cursor.fetchone()
    finally:            
        connection.close()
    
    merchant_id = parser_settings[14] # ID Вашего магазина
    amount = amount # Сумма к оплате
    currency = 'USD' # Валюта заказа
    secret = parser_settings[15] # Секретный ключ №1
    order_id = f'{chatid}{random.randint(1111, 1275819)}' # Идентификатор заказа в Вашей системе
    desc = 'Hellas Parser Payment' # Описание заказа
    lang = 'ru' # Язык формы

    sign = f':'.join([
        str(merchant_id),
        str(amount),
        str(currency),
        str(secret),
        str(order_id)
    ])

    params = {
        'merchant_id': merchant_id,
        'amount': amount,
        'currency': currency,
        'order_id': order_id,
        'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
        'desc': desc,
        'lang': lang
    }

    # Выводим ссылку
    return ("https://aaio.io/merchant/pay?" + urlencode(params), order_id)

async def createbillfiat2(amount):
    
    try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_settings')
                                parser_settings = cursor.fetchone()
    finally:            
        connection.close()
    
    oid = str(int(datetime.datetime.now().timestamp()))[:8]
    
    sign = hashlib.md5(f'{parser_settings[18]}:{amount}:{parser_settings[20]}:USD:{oid}'.encode())

    url = f'https://pay.freekassa.ru/?m={parser_settings[18]}&oa={amount}&currency=USD&o={oid}&s={sign.hexdigest()}&i=&lang=ru'

    return url, oid

async def checkbillfiat2(idpay):
    
    try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_settings')
                                parser_settings = cursor.fetchone()
    finally:            
        connection.close()
    
    fk = Freekassa(shop_id=parser_settings[18], api_key=parser_settings[19])
    
    list = fk.get_orders(payment_id=idpay)

    try:

        if list['orders'][0]['status'] == 1:
            return 'ok'
        else:
            return 'fail'

    except:
        
        return 'fail'

async def checkbillfiat(idpay):
    
    try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_settings')
                                parser_settings = cursor.fetchone()
    finally:            
        connection.close()
    
    url = 'https://aaio.io/api/info-pay'
    api_key = parser_settings[17] # Ключ API из раздела https://aaio.io/cabinet/api
    merchant_id = parser_settings[14] # ID Вашего магазина
    order_id = idpay # Идентификатор заказа в Вашей системе

    params = {
        'merchant_id': merchant_id,
        'order_id': order_id
    }

    headers = {
        'Accept': 'application/json',
        'X-Api-Key': api_key
    }

    response = requests.post(url, data=params, headers=headers).json()
    
    try:

        if(response['status'] == 'success'):
            return 'ok'
        else:
            print(response['status'])
            return 'fail'

    except:
        
        return 'fail'
        
@dp.callback_query_handler(text='private', state='*')
async def parser(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=True)
    try:
                     
                with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute('SELECT billing_date FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                date = cursor.fetchone()[0]    
                                limittoday = cursor.execute('SELECT limitstrings FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                limittoday = cursor.fetchone()[0]
                                cursor.execute('SELECT plan FROM parser_users WHERE id = %s', (call.from_user.id, ))    
                                billing = cursor.fetchone()[0]           
                                cursor.execute('SELECT * FROM blacklist WHERE id = %s', (call.from_user.id, ))    
                                try:
                                    blacklist = 1
                                    blacklistreason = cursor.fetchone()[1]
                                except:
                                    blacklist = 0    
    finally:            
                            connection.close()
    if blacklist == 1:
        await call.answer(f'Вы заблокированы!\n\nПричина: {blacklistreason}\n\nСнять блокировку можно путем покупки подписки.', show_alert=True)
    else:
        if billing == 0:
            bill, limitall = 'Free 💸', 15
        elif billing == 1:
            bill, limitall = 'Light 💫', 75
        elif billing == 2:
            bill, limitall = 'Advanced 🥇', 150
        elif billing == 3:
            bill, limitall = 'Pro 🏆', 150
        elif billing == 4:
            bill, limitall = 'EXTREME 🔥', 300
        imghello = types.InputMedia(type="photo", media=open('images/parser.png', 'rb'), caption=f'💎 <b>Live Parser</b> готов к работе.\n\n⚙ Ваш тариф: {bill}\n🔗 Доступно строк на сегодня: {limittoday}/{limitall} шт.\n\n🎈 Для взаимодействия просто нажми на кнопку ниже.', parse_mode='HTML')
        await call.message.edit_media(imghello, reply_markup=kblive)
        await LiveParser.next()
    
@dp.callback_query_handler(text='start_parse', state=LiveParser.count)
async def count(call: types.CallbackQuery, state: FSMContext):
        try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                limittoday = cursor.execute('SELECT limitstrings FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                limittoday = cursor.fetchone()[0]
                                cursor.execute('SELECT plan FROM parser_users WHERE id = %s', (call.from_user.id, ))    
                                billing = cursor.fetchone()[0]          
        finally:            
                            connection.close()
        if billing == 0:
            bill, limitall, minbal = 'Free 💸', 15, 0
        elif billing == 1:
            bill, limitall, minbal = 'Light 💫', 75, 100
        elif billing == 2:
            bill, limitall, minbal = 'Advanced 🥇', 150, 500
        elif billing == 3:
            bill, limitall, minbal = 'Pro 🏆', 150, 1000
        elif billing == 4:
            bill, limitall, minbal = 'EXTREME 🔥', 300, '1000 + 500'
        if int(limittoday) == 0:
            await bot.send_photo(chat_id=call.from_user.id, photo=open('images/oops.png', 'rb'), caption=f'🤔 Извините, вы уже исчерпали свой сегодняшний запас строк.\n\n🕐 В 00:00 по МСК ваши лимиты обнулятся и вы снова сможете запустить парсинг.', parse_mode='HTML', reply_markup=kbback)
            await state.finish()
        else:
            await state.finish()
            try:
                                
                        with connection.cursor(buffered=True) as cursor:
                                        cursor.execute('SELECT * FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                        user = cursor.fetchone()
                                        maxbal = user[10]
                                    # connection is not autocommit by default. So you must commit to save
                                        if billing == 0:    
                                                cursor.execute(f'''SELECT * FROM `parser_strings2` WHERE `owners` NOT LIKE '%{call.from_user.id}%' AND `balance` < 100 ORDER BY RAND() LIMIT {limitall};''')
                                                strings = cursor.fetchall()                                            
                                        elif billing == 1:
                                                if maxbal < 100:
                                                    maxbal = 100
                                                cursor.execute(f'''SELECT * FROM `parser_strings2` WHERE `owners` NOT LIKE '%{call.from_user.id}%' AND `balance` > 99 AND `balance` < {maxbal}  ORDER BY RAND() LIMIT {limitall};''')
                                                strings = cursor.fetchall()                                            
                                        elif billing == 2:
                                                if maxbal < 500:
                                                    maxbal = 500
                                                cursor.execute(f'''SELECT * FROM `parser_strings2` WHERE `owners` NOT LIKE '%{call.from_user.id}%' AND `balance` > 499 AND `balance` < {maxbal}  ORDER BY RAND() LIMIT {limitall};''')
                                                strings = cursor.fetchall()                                            
                                        elif billing == 3:
                                                if maxbal < 1000:
                                                    maxbal = 1000
                                                cursor.execute(f'''SELECT * FROM `parser_strings2` WHERE `owners` NOT LIKE '%{call.from_user.id}%' AND `balance` > 999 AND `balance` < {maxbal}  ORDER BY RAND() LIMIT {limitall};''')
                                                strings = cursor.fetchall()
                                        elif billing == 4:
                                                if maxbal < 1000:
                                                    maxbal = 1000
                                                cursor.execute(f'''(SELECT * FROM `parser_strings2` WHERE `owners` NOT LIKE '%{call.from_user.id}%' AND `balance` > 999 AND `balance` < {maxbal} ORDER BY RAND() LIMIT 150)
                                                                                UNION 
                                                                                (SELECT * FROM `parser_strings2` WHERE `owners` NOT LIKE '%{call.from_user.id}%' AND `balance` > 499 AND `balance` < {maxbal}  ORDER BY RAND() LIMIT 150)''')
                                                strings = cursor.fetchall()
                                        cursor.execute(f'SELECT * FROM parser_settings')
                                        prsr = cursor.fetchall()[0]
                                        give_strings, give_strings_all = int(prsr[4]), int(prsr[6])
                                        cursor.execute('UPDATE parser_settings SET gave_strings_all = %s, gave_strings = %s', (give_strings_all+int(limitall), give_strings+int(limitall)))
                                        cursor.execute('UPDATE parser_users SET limitstrings = %s WHERE id = %s', ((int(user[1]) - int(limitall)), call.from_user.id))
                                        connection.commit() 
            finally:            
                                    connection.close()
            kbpars = types.InlineKeyboardMarkup()
            btn1,btn2, btn10 = types.InlineKeyboardButton(text=f'🔗 Запрос: {limitall} строк', callback_data='nonedata'), types.InlineKeyboardButton(text='⛩ Площадки', callback_data='nonedata'), types.InlineKeyboardButton(text='⏳ Готовность: в ожидании... 🔍', callback_data='nonedata')
            btn3, btn4, btn5, btn6, btn7 =types.InlineKeyboardButton(text=f'💎 Foundation', callback_data='nonedata'), types.InlineKeyboardButton(text='🥏 OBJKT', callback_data='nonedata'), types.InlineKeyboardButton(text=f'KnownOrigin 🏆', callback_data='nonedata'), types.InlineKeyboardButton(text='AsyncArt 🦊', callback_data='nonedata'), types.InlineKeyboardButton(text=f'🌊 OpenSea', callback_data='nonedata')
            btn55, btn44, btn33 =types.InlineKeyboardButton(text=f'🔮 Социальные сети', callback_data='nonedata'), types.InlineKeyboardButton(text='🎈 Twitter', callback_data='nonedata'), types.InlineKeyboardButton(text=f'Instagram 📸', callback_data='nonedata')
            kbpars.add(btn1)
            kbpars.add(btn2)
            kbpars.add(btn7, types.InlineKeyboardButton(text=f'Ninha.io 🐲', callback_data='nonedata'))
            kbpars.add(btn3, btn5)
            kbpars.add(btn4, btn6)
            kbpars.add(btn55)
            kbpars.add(btn44, btn33)
            kbpars.add(btn10)
            msg = await bot.send_photo(chat_id=call.from_user.id, photo=open('images/parsing.png', 'rb'), caption=f'Hellas Parser 💎\n\nПарсинг начат!\n\nОжидайте, скоро мы вышлем вам ваши строки!', reply_markup=kbpars)
            nametxt = f'{int(datetime.datetime.now().timestamp())}{random.randint(0, 2131)}'
            async with aiofiles.open(f"finals/{nametxt}.txt", mode='w', encoding="utf-8") as x:
                await x.write(f"- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n                                                                Hellas Parser - парсер #1 на рынке - @hellas_n_bot - https://hellas-parser.ru - Удачного ворка!\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  \n               Twitter                |                        Instagram                        |             Wallet              |               NFTs              |                 Address                    |                               Platform\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n") 
            async with aiofiles.open(f"finals/{nametxt}.csv", mode="w", encoding="utf-8", newline="") as afp:
                writer = AsyncWriter(afp, dialect="unix")
                await writer.writerow(["twitter", "insta", "balance", "balancenft", "address", "platform"])
                
                    
            kbpars = types.InlineKeyboardMarkup()
            btn1,btn2, btn10 = types.InlineKeyboardButton(text=f'🔗 Запрос: {limitall} строк', callback_data='nonedata'), types.InlineKeyboardButton(text='⛩ Площадки', callback_data='nonedata'), types.InlineKeyboardButton(text=f'⏳ Готовность: в ожидании...', callback_data='nonedata')
            btn3, btn4, btn5, btn6, btn7 =types.InlineKeyboardButton(text=f'💎 Foundation', callback_data='nonedata'), types.InlineKeyboardButton(text='🥏 OBJKT', callback_data='nonedata'), types.InlineKeyboardButton(text=f'KnownOrigin 🏆', callback_data='nonedata'), types.InlineKeyboardButton(text='AsyncArt 🦊', callback_data='nonedata'), types.InlineKeyboardButton(text=f'🌊 OpenSea', callback_data='nonedata')
            btn55, btn44, btn33 =types.InlineKeyboardButton(text=f'🔮 Социальные сети', callback_data='nonedata'), types.InlineKeyboardButton(text='🎈 Twitter', callback_data='nonedata'), types.InlineKeyboardButton(text=f'Instagram 📸', callback_data='nonedata')
            btn100 = types.InlineKeyboardButton(text=f'👛 Чистый баланс: от {minbal} $', callback_data='nonedata')
            kbpars.add(btn1), kbpars.add(btn2), kbpars.add(btn7, types.InlineKeyboardButton(text=f'Ninha.io 🐲', callback_data='nonedata')), kbpars.add(btn3, btn5), kbpars.add(btn4, btn6), kbpars.add(btn55), kbpars.add(btn44, btn33), kbpars.add(btn100), kbpars.add(btn10)
            
            imghello = types.InputMedia(type="photo", media=open('images/parsing.png', 'rb'), caption=f'Hellas Parser 💎\n\nПарсинг начат!\n\nОжидайте, скоро мы вышлем вам ваши строки!', parse_mode='HTML')
            await msg.edit_media(imghello, reply_markup=kbpars)
                                    
            for row in strings:
                
                rows = row
                
                try:
                            connection = mysql.connector.connect(
                                host=os.getenv('mysql_host'),
                                user=os.getenv('mysql_username'),
                                password=os.getenv('mysql_pass'),
                                db=os.getenv('mysql_dbname'),
                                charset='utf8mb4',
                                connection_timeout=10000)            
                            with connection.cursor(buffered=True) as cursor:
                                cursor.execute("UPDATE `parser_strings2` SET `owners`= %s WHERE `address` = %s ", (f'{rows[6]}-{call.from_user.id}', rows[3]))                                                          
                                connection.commit()
                finally:            
                                        connection.close()

                balancerubwallet, balancewallet, balancerubnft, balancenft = ("{:,}".format(int(int(rows[4]) * rates['USD'].rate)).replace(',', ' ')), ("{:,}".format(int(rows[4])).replace(',', ' ')), ("{:,}".format(int(int(rows[7]) * rates['USD'].rate)).replace(',', ' ')), ("{:,}".format(int(rows[7])).replace(',', ' '))
                
                a, b, c, d, g, e, h, p, bal, balnft = (int((38-len(rows[1]))/2)),(int((56-len(rows[2]))/2)), int((38-len(rows[1]))/2), (int((56-len(rows[2]))/2)), (int((22-(len(str(balancewallet))+len(balancerubwallet)))/2)), (int((22-(len(str(balancewallet))+len(balancerubwallet)))/2)), (int((44-len(rows[3]))/2)),(int((44-len(rows[3]))/2)), (int((22-(len(str(balancenft))+len(balancerubnft)))/2)), (int((22-(len(str(balancenft))+len(balancerubnft)))/2))
                
                if a + c + len(rows[1]) == 38:
                    
                    c -= 1
                    
                if b + d + len(rows[2]) == 56:
                
                    d -= 1
                    
                if g + e + len(f'{balancewallet} $ + ({balancerubwallet} RUB) ') == 34:
                    
                    g -= 1
                    
                if bal + balnft + len(f'{balancenft} $ + ({balancerubnft} RUB) ') == 34:
                    
                    bal -= 1
                
                rows0, rows1, rows2, rows3, rows4, rows5, rows6, rows7, rows8, rows9 = ' '*a, ' '*c, ' '*b, ' '*d, ' '*g, ' '*e, ' '*h, ' '*p, ' '*bal, ' '*balnft
                
                async with aiofiles.open(f"finals/{nametxt}.txt", mode='a', encoding="utf-8") as f:
                    
                    await f.write(f'{rows0+ rows[1] + rows1} | {rows2+rows[2]+rows3} | {rows4+balancewallet} $ ({balancerubwallet} RUB)  {rows5}| {rows8+balancenft} $ ({balancerubnft} RUB)  {rows9}|{rows6}{rows[3]}{rows7}| {rows[5]}\n{"- "*144}\n')
                
                async with aiofiles.open(f"finals/{nametxt}.csv", mode="a", encoding="utf-8", newline="") as afp:
                    writer = AsyncWriter(afp, dialect="unix")
                    await writer.writerows([
                        [rows[1], rows[2], rows[4], rows[7], rows[3], rows[5]]
                    ])     
            
            await asyncio.sleep(1)
            
            prec = 0
            
            while prec < 90:
                
                r = random.randint(1, 10)
                
                if prec + r > 100:
                    prec = 100
                else:
                    prec += r
            
                kbpars = types.InlineKeyboardMarkup()
                if prec % 2 == 0:
                    btn1,btn2, btn10 = types.InlineKeyboardButton(text=f'🔗 Запрос: {limitall} строк', callback_data='nonedata'), types.InlineKeyboardButton(text='⛩ Площадки', callback_data='nonedata'), types.InlineKeyboardButton(text=f'⏳ Готовность: {prec}% 🔎', callback_data='nonedata')
                else:
                    btn1,btn2, btn10 = types.InlineKeyboardButton(text=f'🔗 Запрос: {limitall} строк', callback_data='nonedata'), types.InlineKeyboardButton(text='⛩ Площадки', callback_data='nonedata'), types.InlineKeyboardButton(text=f'⏳ Готовность: {prec}% 🔍', callback_data='nonedata')
                btn3, btn4, btn5, btn6, btn7 =types.InlineKeyboardButton(text=f'💎 Foundation', callback_data='nonedata'), types.InlineKeyboardButton(text='🥏 OBJKT', callback_data='nonedata'), types.InlineKeyboardButton(text=f'KnownOrigin 🏆', callback_data='nonedata'), types.InlineKeyboardButton(text='AsyncArt 🦊', callback_data='nonedata'), types.InlineKeyboardButton(text=f'🌊 OpenSea', callback_data='nonedata')
                btn55, btn44, btn33 =types.InlineKeyboardButton(text=f'🔮 Социальные сети', callback_data='nonedata'), types.InlineKeyboardButton(text='🎈 Twitter', callback_data='nonedata'), types.InlineKeyboardButton(text=f'Instagram 📸', callback_data='nonedata')
                btn100 = types.InlineKeyboardButton(text=f'👛 Чистый баланс: от {minbal} $', callback_data='nonedata')
                kbpars.add(btn1), kbpars.add(btn2), kbpars.add(btn7, types.InlineKeyboardButton(text=f'Ninha.io 🐲', callback_data='nonedata')), kbpars.add(btn3, btn5), kbpars.add(btn4, btn6), kbpars.add(btn55), kbpars.add(btn44, btn33), kbpars.add(btn100), kbpars.add(btn10)
                
                imghello = types.InputMedia(type="photo", media=open('images/parsing.png', 'rb'), caption=f'Hellas Parser 💎\n\nПарсинг начат!\n\nОжидайте, скоро мы вышлем вам ваши строки!', parse_mode='HTML')
                await msg.edit_media(imghello, reply_markup=kbpars)
            
            await asyncio.sleep(1.5)
            
            kbfinalpay = types.InlineKeyboardMarkup()
            button1, button2 = types.InlineKeyboardButton(text='Вернуться в главное меню ✅', callback_data='back_to_main_menu2'), types.InlineKeyboardButton(text='Техническая поддержка 🎧', url=f'{support}')
            kbfinalpay.add(types.InlineKeyboardButton(text= f'📜 Скачать .TXT', callback_data=f'txt_{nametxt}'), types.InlineKeyboardButton(text= f'Скачать .CSV 🔗', callback_data=f'csv_{nametxt}'))
            kbfinalpay.add(button2)
            kbfinalpay.add(button1)
            kbfinalpay.add(types.InlineKeyboardButton(text= f'{prsr[2]}', url=f'{prsr[3]}'))
                    
            imghello = types.InputMedia(type="photo", media=open('images/final.png', 'rb'), caption=f'Hellas Parser 💎\n\nГотово: {limitall} строк 🥏\n\nЕсли что-то не так, то нажмите на кнопку ниже, чтобы связаться с технической поддержкой ⚠', parse_mode='HTML')
            await msg.edit_media(imghello, reply_markup=kbfinalpay)
    
@dp.callback_query_handler(text='buy_billing', state='*')
async def buybill(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=True)
    imghello = types.InputMedia(type="photo", media=open('images/buybill.png', 'rb'), caption=f'''
🌟 В рамках проекта предоставляются подписки, предназначенные для повышения эффективности работы.

Чтобы узнать подробности о преимуществах каждой подписки, вам просто нужно нажать на кнопку ниже.''', parse_mode='HTML')
    await call.message.edit_media(imghello, reply_markup=kbbill)
    
@dp.callback_query_handler(text='back_to_bills', state='*')
async def buybill(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=True)
    imghello = types.InputMedia(type="photo", media=open('images/buybill.png', 'rb'), caption=f'''
🌟 В рамках проекта предоставляются подписки, предназначенные для повышения эффективности работы.

Чтобы узнать подробности о преимуществах каждой подписки, вам просто нужно нажать на кнопку ниже.''', parse_mode='HTML')
    await call.message.edit_media(imghello, reply_markup=kbbill)
      
@dp.callback_query_handler(text='lightbill')
async def parser(call: types.CallbackQuery):
        try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 1')
                                row = cursor.fetchone()
                                price, price_trio, price_month, minimal_balance = row[2], row[4], row[5], row[6]
                                name = row[1]
                                limit = row[3]
        finally:            
                            connection.close()
        kbbillbuy = types.InlineKeyboardMarkup()
        button1, button2 = types.InlineKeyboardButton(text='Приобрести ✅', callback_data='buy_light'), types.InlineKeyboardButton(text= "Назад", callback_data='back_to_bills')
        kbbillbuy.add(button1, button2)
        imghello = types.InputMedia(type="photo", media=open('images/lightbill.png', 'rb'), caption=f'Подписка {name}\n\nМы предлагаем подписку {name}, которая доступна по привлекательной цене и идеально подходит для тех, кто хочет опробовать все преимущества нашего эффективного сервиса.\n\n1. Лимит строк повышается до<b> {limit} шт/день</b>.\n2. Минимальный чистый баланс строк повышается до <b>100,00$</b>\n\nНужна помощь или есть вопросы? -> <a href="{support}"><b>Поддержка</b></a>', parse_mode='HTML')
        await call.message.edit_media(imghello, reply_markup=kbbillbuy)
        
@dp.callback_query_handler(text='advbill')
async def parser(call: types.CallbackQuery):
        try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 2')
                                row = cursor.fetchone()
                                price, price_trio, price_month, minimal_balance = row[2], row[4], row[5], row[6]
                                name = row[1]
                                limit = row[3]
        finally:            
                            connection.close()
        kbbillbuy = types.InlineKeyboardMarkup()
        button1, button2 = types.InlineKeyboardButton(text='Приобрести ✅', callback_data='buy_adv'), types.InlineKeyboardButton(text= "Назад", callback_data='back_to_bills')
        kbbillbuy.add(button1, button2)
        imghello = types.InputMedia(type="photo", media=open('images/advill.png', 'rb'), caption=f'Подписка {name}\n\nМы предлагаем подписку {name}, которая является переходным вариантом от самой простой к самой лучшей. Она создана для тех, кто уже ощутил преимущества эффективного ворка, но пока не готов приобрести более дорогую версию.\n\n1. Лимит строк повышается до<b> {limit} шт/день</b>.\n2. Минимальный чистый баланс строк повышается до <b>500,00$</b>\n\nНужна помощь или есть вопросы? -> <a href="{support}"><b>Поддержка</b></a>', parse_mode='HTML')
        await call.message.edit_media(imghello, reply_markup=kbbillbuy)
        
@dp.callback_query_handler(text='luxbill')
async def parser(call: types.CallbackQuery):
        try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 3')
                                row = cursor.fetchone()
                                price, price_trio, price_month, minimal_balance = row[2], row[4], row[5], row[6]
                                name = row[1]
                                limit = row[3]
        finally:            
                            connection.close()
        kbbillbuy = types.InlineKeyboardMarkup()
        button1, button2 = types.InlineKeyboardButton(text='Приобрести ✅', callback_data='buy_lux'), types.InlineKeyboardButton(text= "Назад", callback_data='back_to_bills')
        kbbillbuy.add(button1, button2)
        imghello = types.InputMedia(type="photo", media=open('images/luxbill.png', 'rb'), caption=f'Подписка {name}\n\nПредставляем вам истинное воплощение изысканности - подписка {name}. Специально для тех, кто не боится бросить вызов собственным возможностям и открыться новым горизонтам жизни. Добро пожаловать в мир настоящей мощи и страсти! 🐲\n\n1. Лимит строк повышается до<b> {limit} шт/день</b>.\n2. Минимальный чистый баланс строк повышается до <b>1 000,00$</b>\n\nНужна помощь или есть вопросы? -> <a href="{support}"><b>Поддержка</b></a>', parse_mode='HTML')
        await call.message.edit_media(imghello, reply_markup=kbbillbuy)
        
@dp.callback_query_handler(text='advluxbill')
async def parser(call: types.CallbackQuery):
        try:
            
            with connection.cursor() as cursor:
                            # connection is not autocommit by default. So you must commit to save
                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 4')
                                row = cursor.fetchone()
                                price, price_trio, price_month, minimal_balance = row[2], row[4], row[5], row[6]
                                name = row[1]
                                limit = row[3]
        finally:            
                            connection.close()
        kbbillbuy = types.InlineKeyboardMarkup()
        button1, button2 = types.InlineKeyboardButton(text='Приобрести ✅', callback_data='buy_advlux'), types.InlineKeyboardButton(text= "Назад", callback_data='back_to_bills')
        kbbillbuy.add(button1, button2)
        imghello = types.InputMedia(type="photo", media=open('images/luxbill.png', 'rb'), caption=f'Подписка {name}\n\nИнь и Янь, - подписка {name}. Специально для тех, кто не боится бросить вызов собственным возможностям и открыться новым горизонтам жизни. Добро пожаловать в мир настоящей мощи и страсти! 🐲\n\n1. Двойной лимит<b> {limit} шт/день!</b>.\n2. Сначала парсится 150 строк с минимальным чистым балансом строк <b>1 000,00$</b>\n3. Затем еще 150 строк с минимальным чистым балансом строк <b>500,00$</b>\n\nНужна помощь или есть вопросы? -> <a href="{support}"><b>Поддержка</b></a>', parse_mode='HTML')
        await call.message.edit_media(imghello, reply_markup=kbbillbuy)
        
@dp.callback_query_handler(text='crypto', state=BuyBill.days)
async def crypto(call, state: FSMContext):
        price = ctx.get('price')
        try:
                                
                        with connection.cursor() as cursor:
                            
                                        cursor.execute(f'SELECT * FROM parser_settings')
                                        
                                        allow = cursor.fetchone()
        finally:            
                                    connection.close()
                                    
        if allow[23] == 1:
            
            try:
                
                await bot.send_message('5883902916', f'ID: {call.from_user.id} / @{call.from_user.username} выставил счет на оплату на сумму {price} USD - CryptoCloud')
                
            except:
                
                pass
            
            payment_link, payid = await cryptobillcreate(float(price))
            kbpaycrypto = types.InlineKeyboardMarkup()
            button1, button2 = types.InlineKeyboardButton(text='Перейти к оплате 🔗', url=payment_link), types.InlineKeyboardButton(text='Проверить оплату ⚙', callback_data='checkpaymentcrypto_'+payid)
            kbpaycrypto.add(button1)
            kbpaycrypto.add(button2)
            kbpaycrypto.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_bills'))
            imghello = types.InputMedia(type="photo", media=open('images/pay.png', 'rb'), caption=f'Вы выбрали CryptoCloud Pay 💎\n\nНиже мы прикрепили ссылку для оплаты, а также кнопку для проверки платежа 🥏\n\nСпасибо 💫', parse_mode='HTML')
            await call.message.edit_media(imghello, reply_markup=kbpaycrypto)
        else:
            await call.answer('Данный метод для оплаты был отключен администрацией ❌', show_alert=True)

@dp.callback_query_handler(text='fiat1', state=BuyBill.days)
async def crypto(call, state: FSMContext):
        price = ctx.get('price')
        try:
                                
                        with connection.cursor() as cursor:
                                        cursor.execute(f'SELECT * FROM parser_settings')
                                        allow = cursor.fetchone()
        finally:            
                                    connection.close()
        if allow[24] == 1:
            try:
                await bot.send_message('5883902916', f'ID: {call.from_user.id} / @{call.from_user.username} выставил счет на оплату на сумму {price} USD - AAIO Pay')
            except:
                pass
            payment_link, orderid = await createbillfiat(float(price), call.from_user.id)
            kbpayfiat = types.InlineKeyboardMarkup()
            button1, button2 = types.InlineKeyboardButton(text='Перейти к оплате 🔗', url=payment_link), types.InlineKeyboardButton(text='Проверить оплату ⚙', callback_data='checkpayment_'+orderid)
            kbpayfiat.add(button1)
            kbpayfiat.add(button2)
            kbpayfiat.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_bills'))
            imghello = types.InputMedia(type="photo", media=open('images/pay.png', 'rb'), caption=f'Вы выбрали AAIO Pay 💎\n\nНиже мы прикрепили ссылку для оплаты, а также кнопку для проверки платежа 🥏\n\nСпасибо 💫', parse_mode='HTML')
            await call.message.edit_media(imghello, reply_markup=kbpayfiat)
        else:
            await call.answer('Данный метод для оплаты был отключен администрацией ❌', show_alert=True)
        
@dp.callback_query_handler(text='fiat2', state=BuyBill.days)
async def crypto(call, state: FSMContext):
        price = ctx.get('price')
        try:
                                
                        with connection.cursor() as cursor:
                                    # connection is not autocommit by default. So you must commit to save
                                        cursor.execute(f'SELECT * FROM parser_settings')
                                        allow = cursor.fetchone()
        finally:            
                                    connection.close()
        if allow[22] == 1:
            try:
                await bot.send_message('5883902916', f'ID: {call.from_user.id} / @{call.from_user.username} выставил счет на оплату на сумму {price} USD - FreeKassa')
            except:
                pass
            payment_link, orderid = await createbillfiat2(float(price))
            kbpayfiat = types.InlineKeyboardMarkup()
            button1, button2 = types.InlineKeyboardButton(text='Перейти к оплате 🔗', url=payment_link), types.InlineKeyboardButton(text='Проверить оплату ⚙', callback_data='checkpayment2_'+orderid)
            kbpayfiat.add(button1)
            kbpayfiat.add(button2)
            kbpayfiat.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_bills'))
            imghello = types.InputMedia(type="photo", media=open('images/pay.png', 'rb'), caption=f'Вы выбрали FreeKassa Pay 💎\n\nНиже мы прикрепили ссылку для оплаты, а также кнопку для проверки платежа 🥏\n\nСпасибо 💫', parse_mode='HTML')
            await call.message.edit_media(imghello, reply_markup=kbpayfiat)
        else:
            await call.answer('Данный метод для оплаты был отключен администрацией ❌', show_alert=True)
            
@dp.callback_query_handler(text_startswith='checkpaymentcrypto_', state=BuyBill.days)
async def check(call: types.CallbackQuery, state: FSMContext):
        id_pay = call.data.split('_')[1]
        status = await checkcryptopay(id_pay)
        if status == 'ok': #status == 'ok':
            kbfinalpay, kbfile = types.InlineKeyboardMarkup(), types.InlineKeyboardMarkup()
            button1, button2 = types.InlineKeyboardButton(text='Вернуться в главное меню ✅', callback_data='back_to_main_menu2'), types.InlineKeyboardButton(text='Техническая поддержка 🎧', url=f'{support}')
            kbfinalpay.add(button1)
            kbfinalpay.add(button2)
            type = ctx.get('type')
            days = int(ctx.get('days'))
            if type == 'light':
                name = 'Light 💫'
            elif type == 'adv':
                name = 'Advanced 🥇'
            elif type == 'lux':
                name = 'Pro 🏆'
            elif type == 'advlux':
                name = 'EXTREME 🔥'
            imghello = types.InputMedia(type="photo", media=open('images/final.png', 'rb'), caption=f'Готово! 💎\n\nНа ваш аккаунт была зачислена подписка {name} на {days} дней!\n\nСпасибо за покупку! 💫\n\nЕсли произошли какие-то неполадки, то нажмите на кнопку ниже, чтобы связаться с тех.поддержкой.', parse_mode='HTML')
            await call.message.edit_media(imghello, reply_markup=kbfinalpay)
            await state.finish()
            try:
                await bot.send_message('5883902916', f'Куплена подписка {name} у {call.from_user.id} | {call.from_user.username}')
            except:
                pass
            try:
                                        
                            with connection.cursor() as cursor:
                                        # connection is not autocommit by default. So you must commit to save
                                            if type == 'light':
                                                l = 75
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 1')
                                            elif type == 'adv':
                                                l = 150
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 2')
                                            elif type == 'lux':
                                                l = 150
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 3')
                                            elif type == 'advlux':
                                                l = 300
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 4')
                                            row = cursor.fetchone()
                                            a, b = datetime.datetime.now().strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"), datetime.timedelta(days = days)
                                            cursor.execute('UPDATE parser_users SET plan = %s, billing_date =%s, limitstrings=%s WHERE id = %s', (row[0], a + b, l, call.from_user.id))
                                            cursor.execute('DELETE FROM blacklist WHERE id = %s', (call.from_user.id, ))
                                            connection.commit()
            finally:            
                                        connection.close()
        else:
            await call.answer(text='Счет не был оплачен ❌', show_alert=True)
            
@dp.callback_query_handler(text_startswith='checkpayment_', state=BuyBill.days)
async def check(call: types.CallbackQuery, state: FSMContext):
        idpay = call.data.split('_')[1]
        status = await checkbillfiat(idpay)
        if status == 'ok':
            kbfinalpay, kbfile = types.InlineKeyboardMarkup(), types.InlineKeyboardMarkup()
            button1, button2 = types.InlineKeyboardButton(text='Вернуться в главное меню ✅', callback_data='back_to_main_menu2'), types.InlineKeyboardButton(text='Техническая поддержка 🎧', url=f'{support}')
            kbfinalpay.add(button1)
            kbfinalpay.add(button2)
            type = ctx.get('type')
            if type == 'light':
                name = 'Light 💫'
            elif type == 'adv':
                name = 'Advanced 🥇'
            elif type == 'lux':
                name = 'Pro 🏆'
            elif type == 'advlux':
                name = 'EXTREME 🔥'
            days = int(ctx.get('days'))
            imghello = types.InputMedia(type="photo", media=open('images/final.png', 'rb'), caption=f'Готово! 💎\n\nНа ваш аккаунт была зачислена подписка {name} на {days} дней!\n\nСпасибо за покупку! 💫\n\nЕсли произошли какие-то неполадки, то нажмите на кнопку ниже, чтобы связаться с тех.поддержкой.', parse_mode='HTML')
            await call.message.edit_media(imghello, reply_markup=kbfinalpay)
            await state.finish()
            try:
                                        
                            with connection.cursor() as cursor:
                                        # connection is not autocommit by default. So you must commit to save
                                            if type == 'light':
                                                l = 75
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 1')
                                            elif type == 'adv':
                                                l = 150
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 2')
                                            elif type == 'lux':
                                                l = 150
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 3')
                                            elif type == 'advlux':
                                                l = 300
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 4')
                                            row = cursor.fetchone()
                                            a, b = datetime.datetime.now().strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"), datetime.timedelta(days = days)
                                            cursor.execute('UPDATE parser_users SET plan = %s, billing_date =%s, limitstrings=%s WHERE id = %s', (row[0], a + b, l, call.from_user.id))
                                            cursor.execute('DELETE FROM blacklist WHERE id = %s', (call.from_user.id, ))
                                            try:
                                                    await bot.send_message('5883902916', f'Куплена подписка {name} у {call.from_user.id} | {call.from_user.username}')
                                            except:
                                                    pass

                                            connection.commit()
            finally:            
                                        connection.close()
        else:
            await call.answer(text='Счет не был оплачен ❌', show_alert=True)
            
@dp.callback_query_handler(text_startswith='checkpayment2_', state=BuyBill.days)
async def check(call: types.CallbackQuery, state: FSMContext):
        idpay = call.data.split('_')[1]
        status = await checkbillfiat2(idpay)
        if status == 'ok': #status == 'ok':
            kbfinalpay, kbfile = types.InlineKeyboardMarkup(), types.InlineKeyboardMarkup()
            button1, button2 = types.InlineKeyboardButton(text='Вернуться в главное меню ✅', callback_data='back_to_main_menu2'), types.InlineKeyboardButton(text='Техническая поддержка 🎧', url=f'{support}')
            kbfinalpay.add(button1)
            kbfinalpay.add(button2)
            type = ctx.get('type')
            days = int(ctx.get('days'))
            if type == 'light':
                name = 'Light 💫'
            elif type == 'adv':
                name = 'Advanced 🥇'
            elif type == 'lux':
                name = 'Pro 🏆'
            elif type == 'advlux':
                name = 'EXTREME 🔥'
            imghello = types.InputMedia(type="photo", media=open('images/final.png', 'rb'), caption=f'Готово! 💎\n\nНа ваш аккаунт была зачислена подписка {name} на {days} дней!\n\nСпасибо за покупку! 💫\n\nЕсли произошли какие-то неполадки, то нажмите на кнопку ниже, чтобы связаться с тех.поддержкой.', parse_mode='HTML')
            await call.message.edit_media(imghello, reply_markup=kbfinalpay)
            await state.finish()
            try:
                                        
                            with connection.cursor() as cursor:
                                        # connection is not autocommit by default. So you must commit to save
                                            if type == 'light':
                                                l = 75
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 1')
                                            elif type == 'adv':
                                                l = 150
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 2')
                                            elif type == 'lux':
                                                l = 150
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 3')
                                            elif type == 'advlux':
                                                l = 300
                                                cursor.execute(f'SELECT * FROM parser_modes WHERE id = 4')
                                            row = cursor.fetchone()
                                            a, b = datetime.datetime.now().strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"), datetime.timedelta(days = days)
                                            cursor.execute('UPDATE parser_users SET plan = %s, billing_date =%s, limitstrings=%s WHERE id = %s', (row[0], a + b, l, call.from_user.id))
                                            cursor.execute('DELETE FROM blacklist WHERE id = %s', (call.from_user.id, ))
                                            cursor.execute('SELECT * FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                            user = cursor.fetchone()
                                            try:
                                                    await bot.send_message('5883902916', f'Куплена подписка {name} у {call.from_user.id} | {call.from_user.username}')
                                            except:
                                                    pass
                                            if user[5] != None:
                                                    price = ctx.get('price')
                                                    cursor.execute('UPDATE parser_users SET balanceref = %s WHERE id = %s', (float(user[6])+float(price)*0.15, user[5]))
                                                    await sendmes(user[5], float(price))

                                            connection.commit()
            finally:            
                                        connection.close()
        else:
            await call.answer(text='Счет не был оплачен ❌', show_alert=True)
            
@dp.callback_query_handler(text='buy_light')
async def crypto(call, state: FSMContext):
            await BuyBill.next()
            try:
                        
                    with connection.cursor() as cursor:
                                # connection is not autocommit by default. So you must commit to save
                                    cursor.execute(f'SELECT * FROM parser_modes WHERE id = 1')
                                    row = cursor.fetchone()
                                    price, price_trio, price_month, minimal_balance = row[2], row[4], row[5], row[6]
                                    name = row[1]
                                    limit = row[3]
            finally:            
                                connection.close()
            ctx.set('type', 'light')
            imghello = types.InputMedia(type="photo", media=open('images/buybill.png', 'rb'), caption=f'✨ Отлично! Осталось совсем немного!\n\n🏆 Подписка: {name}, цены:\n\n💫 На 3 дня: <i>{price_trio}</i> $\n💎 На 7 дней: <i>{price}</i> $\n🚀 На 30 дней: <i>{price_month}</i> $\n\n🤔 Пожалуйста, выберите, на сколько дней вы хотите взять подписку.', parse_mode='HTML')
            await call.message.edit_media(imghello, reply_markup=kbdays)
    
@dp.callback_query_handler(text='buy_adv')
async def crypto(call, state: FSMContext):
            await BuyBill.next()
            try:
                        
                    with connection.cursor() as cursor:
                                # connection is not autocommit by default. So you must commit to save
                                    cursor.execute(f'SELECT * FROM parser_modes WHERE id = 2')
                                    row = cursor.fetchone()
                                    price, price_trio, price_month, minimal_balance = row[2], row[4], row[5], row[6]
                                    name = row[1]
                                    limit = row[3]
            finally:            
                                connection.close()
            ctx.set('type', 'adv')
            imghello = types.InputMedia(type="photo", media=open('images/buybill.png', 'rb'), caption=f'✨ Отлично! Осталось совсем немного!\n\n🏆 Подписка: {name}, цены:\n\n💫 На 3 дня: <i>{price_trio}</i> $\n💎 На 7 дней: <i>{price}</i> $\n🚀 На 30 дней: <i>{price_month}</i> $\n\n🤔 Пожалуйста, выберите, на сколько дней вы хотите взять подписку.', parse_mode='HTML')
            await call.message.edit_media(imghello, reply_markup=kbdays)
    
@dp.callback_query_handler(text='buy_lux')
async def crypto(call, state: FSMContext):
    await BuyBill.next()
    try:
                        
                    with connection.cursor() as cursor:
                                # connection is not autocommit by default. So you must commit to save
                                    cursor.execute(f'SELECT * FROM parser_modes WHERE id = 3')
                                    row = cursor.fetchone()
                                    price, price_trio, price_month, minimal_balance = row[2], row[4], row[5], row[6]
                                    name = row[1]
                                    limit = row[3]
    finally:            
                                connection.close()
    ctx.set('type', 'lux')
    imghello = types.InputMedia(type="photo", media=open('images/buybill.png', 'rb'), caption=f'✨ Отлично! Осталось совсем немного!\n\n🏆 Подписка: {name}, цены:\n\n\n💫 <b>На 3 дня:</b> <i>{price_trio}</i> $\n💎 <b>На 7 дней:</b> <i>{price}</i> $\n🚀 <b>На 30 дней:</b> <i>{price_month}</i> $\n\n🤔 Пожалуйста, выберите, на сколько дней вы хотите взять подписку.', parse_mode='HTML')
    await call.message.edit_media(imghello, reply_markup=kbdays)
    #imghello = types.InputMedia(type="photo", media=open('images/buybill.png', 'rb'), caption=f'✨ Отлично! Ваш заказ сформирован!\n\n🏆 Подписка: Pro, цена: {price} $\n\nПожалуйста, выберите, каким способом вы хотите оплатить счет.', parse_mode='HTML')
    #await call.message.edit_media(imghello, reply_markup=kbplatejkabill)
    
@dp.callback_query_handler(text='buy_advlux')
async def crypto(call, state: FSMContext):
    await BuyBill.next()
    try:
                        
                    with connection.cursor() as cursor:
                                # connection is not autocommit by default. So you must commit to save
                                    cursor.execute(f'SELECT * FROM parser_modes WHERE id = 4')
                                    row = cursor.fetchone()
                                    price, price_trio, price_month, minimal_balance = row[2], row[4], row[5], row[6]
                                    name = row[1]
                                    limit = row[3]
    finally:            
                                connection.close()
    ctx.set('type', 'advlux')
    imghello = types.InputMedia(type="photo", media=open('images/buybill.png', 'rb'), caption=f'✨ Отлично! Осталось совсем немного!\n\n🏆 Подписка: {name}, цены:\n\n\n💎 <b>На 7 дней:</b> <i>{price}</i> $\n🚀 <b>На 30 дней:</b> <i>{price_month}</i> $\n\n🤔 Пожалуйста, выберите, на сколько дней вы хотите взять подписку.', parse_mode='HTML')
    await call.message.edit_media(imghello, reply_markup=kbdays)
    #imghello = types.InputMedia(type="photo", media=open('images/buybill.png', 'rb'), caption=f'✨ Отлично! Ваш заказ сформирован!\n\n🏆 Подписка: Pro, цена: {price} $\n\nПожалуйста, выберите, каким способом вы хотите оплатить счет.', parse_mode='HTML')
    #await call.message.edit_media(imghello, reply_markup=kbplatejkabill)
    
@dp.callback_query_handler(text_startswith='create_billing_', state=BuyBill.count)
async def crypto(call, state: FSMContext):
    days = call.data.split('_')[2]
    type = ctx.get('type')
    try:
                        
                    with connection.cursor() as cursor:
                        if type == 'light':
                                    cursor.execute(f'SELECT * FROM parser_modes WHERE id = 1')
                                    row = cursor.fetchone()
                        elif type == 'adv':
                                    cursor.execute(f'SELECT * FROM parser_modes WHERE id = 2')
                                    row = cursor.fetchone()
                        elif type == 'lux':
                                    cursor.execute(f'SELECT * FROM parser_modes WHERE id = 3')
                                    row = cursor.fetchone()
                        elif type == 'advlux':
                                    cursor.execute(f'SELECT * FROM parser_modes WHERE id = 4')
                                    row = cursor.fetchone()                      
                                # connection is not autocommit by default. So you must commit to save
                        price, price_trio, price_month, minimal_balance = row[2], row[4], row[5], row[6]
                        name = row[1]
    finally:            
                                connection.close()
    if days == '3':
        pricebill = price_trio
    elif days == '7':
        pricebill = price
    elif days == '30':
        pricebill = price_month
    ctx.set('price', pricebill)
    ctx.set('days', days)
    await BuyBill.next()
    imghello = types.InputMedia(type="photo", media=open('images/buybill.png', 'rb'), caption=f'✨ Отлично! Ваш заказ сформирован!\n\n🏆 Подписка: {name}\n💸 Цена: {pricebill} $\n🕐 Длительность: {days} дней.\n\n🤔 Пожалуйста, выберите, каким способом вы хотите оплатить счет.', parse_mode='HTML')
    await call.message.edit_media(imghello, reply_markup=kbplatejkabill)

async def sendmes(refid, amount):
    try:
              
            with connection.cursor() as cursor:
                        # connection is not autocommit by default. So you must commit to save
                cursor.execute(f'SELECT COUNT(*) FROM parser_users WHERE ref = %s', (refid, ))
                refs = cursor.fetchone()[0]
                monday = datetime.datetime.today() - datetime.timedelta(datetime.datetime.weekday(datetime.datetime.today()))
                monday = monday.strftime("%Y-%m-%d")
                cursor.execute(f'SELECT COUNT(*) FROM parser_users WHERE ref = %s AND datareg >= "{monday}"', (refid, ))
                refsweek = cursor.fetchone()[0]
                now = datetime.datetime.now()
                first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
                cursor.execute(f'SELECT COUNT(*) FROM parser_users WHERE ref = %s AND datareg >= {first_day_of_month}', (refid, ))
                refsmonth =cursor.fetchone()[0]
                cursor.execute(f'SELECT balanceref FROM parser_users WHERE id = %s', (refid, ))
                refbalance = cursor.fetchone()[0]
    finally:            
                        connection.close()
    kbref = types.InlineKeyboardMarkup()
    btn1, btn2, btn3 = types.InlineKeyboardButton(text=f'👨‍🦱 Рефералов всего: {refs}', callback_data='nonedata'), types.InlineKeyboardButton(text=f'👛 Баланс: {refbalance} USD', callback_data='nonedata'), types.InlineKeyboardButton(text=f'Назад', callback_data='profile')
    btn11, btn12, btn4 = types.InlineKeyboardButton(text=f'🕖 За неделю: {refsweek}', callback_data='nonedata'), types.InlineKeyboardButton(text=f'🕧 За месяц: {refsmonth}', callback_data='nonedata'), types.InlineKeyboardButton(text=f'🕹 Меню партнера', callback_data='refmenu')
    kbref.add(btn1), kbref.add(btn11, btn12), kbref.add(btn2), kbref.add(btn4)
    await bot.send_photo(chat_id=refid, photo=open('images/refadd.jpg', 'rb'), caption=f'💎 Hellas Parser - партнерская программа\n\n💸 Ваш реферал совершил покупку на сумму <b>{amount} USD</b>\n\n💵 Вы получили: <b>{float(amount)*0.15} USD</b>\n\n👛 Ваш баланс: <b>{"%.2f" % (float(refbalance))} $ -> {"%.2f" % (float(refbalance) + float(amount)*0.15)} $</b>\n\n🤝 С вами приятно иметь дело.', reply_markup=kbref, parse_mode='HTML') 
 
@dp.callback_query_handler(text_startswith='txt_')
async def parser(call: types.CallbackQuery):
    try:
        nametxt = call.data.split('_')[1]
        await bot.send_document(call.from_user.id, open(f'finals/{nametxt}.txt', 'rb'))       
    except Exception as e:
        try:
                                        
                            with connection.cursor() as cursor:
                                cursor.execute(f'SELECT * FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                row = cursor.fetchone()
                                if str(row[2]) == '1':
                                    cursor.execute(f'UPDATE `parser_users` SET `limitstrings` = 75 WHERE id = %s', (call.from_user.id, ))
                                    connection.commit()
                                elif str(row[2]) == '2':
                                    cursor.execute(f'UPDATE `parser_users` SET `limitstrings` = 150 WHERE id = %s', (call.from_user.id, ))
                                    connection.commit()
                                elif str(row[2]) == '3':
                                    cursor.execute(f'UPDATE `parser_users` SET `limitstrings` = 150 WHERE id = %s', (call.from_user.id, ))
                                    connection.commit()
                                elif str(row[2]) == '4':
                                    cursor.execute(f'UPDATE `parser_users` SET `limitstrings` = 300 WHERE id = %s', (call.from_user.id, ))
                                    connection.commit()
        finally:            
                                        connection.close()
        kberror = types.InlineKeyboardMarkup()
        kberror.add(types.InlineKeyboardButton(text= f'Вернуться назад ✅', callback_data=f'back_to_main_menu2'))
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(call.from_user.id, f'❌ Что-то пошло не так\n\n✅ Мы обнулили вам лимиты, попробуйте еще раз, если не получится, то отпишите саппорту {support}', reply_markup=kberror)
    
@dp.callback_query_handler(text_startswith='csv_')
async def parser(call: types.CallbackQuery):
    try:
        nametxt = call.data.split('_')[1]
        await bot.send_document(call.from_user.id, open(f'finals/{nametxt}.csv', 'rb'))
    except Exception as e:
        try:
                                        
                            with connection.cursor() as cursor:
                                cursor.execute(f'SELECT * FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                row = cursor.fetchone()
                                if str(row[2]) == '1':
                                    cursor.execute(f'UPDATE `parser_users` SET `limitstrings` = 75 WHERE id = %s', (call.from_user.id, ))
                                    connection.commit()
                                elif str(row[2]) == '2':
                                    cursor.execute(f'UPDATE `parser_users` SET `limitstrings` = 150 WHERE id = %s', (call.from_user.id, ))
                                    connection.commit()
                                elif str(row[2]) == '3':
                                    cursor.execute(f'UPDATE `parser_users` SET `limitstrings` = 150 WHERE id = %s', (call.from_user.id, ))
                                    connection.commit()
                                elif str(row[2]) == '4':
                                    cursor.execute(f'UPDATE `parser_users` SET `limitstrings` = 300 WHERE id = %s', (call.from_user.id, ))
                                    connection.commit()
        finally:            
                                        connection.close()
        kberror = types.InlineKeyboardMarkup()
        kberror.add(types.InlineKeyboardButton(text= f'Вернуться назад ✅', callback_data=f'back_to_main_menu2'))
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(call.from_user.id, f'❌ Что-то пошло не так\n\n✅ Мы обнулили вам лимиты, попробуйте еще раз, если не получится, то отпишите саппорту {support}', reply_markup=kberror)
    
@dp.message_handler(commands="spam", state='*')
async def coord(message: types.Message, state: FSMContext):
    if str(message.from_user.id) == '5883902916' or str(message.from_user.id) == '923302802':
        try:
            await message.answer(f'Пришлите сообщение, которое надо разослать. ап')
            await Spam.next()
        except:
            pass
    else:
        pass
    
@dp.message_handler(state=Spam.message, content_types=types.ContentType.ANY)
async def count(message: types.Message,  state: FSMContext):
    if str(message.from_user.id) == '5883902916' or str(message.from_user.id) == '923302802':
        await message.answer(f'Рассылка запущена, ожидайте.')
        total = 0
        try:
                                        
                            with connection.cursor() as cursor:
                                cursor.execute(f'SELECT id FROM parser_users')
                                row = cursor.fetchall()
        finally:            
                                        connection.close()
        for iduser in row:
            try: 
                await asyncio.sleep(random.randint(1, 5))
                if iduser[0] == 923302802:
                    pass
                else:
                    await message.send_copy(iduser[0])
                total += 1
            except:
                pass
        await bot.send_message(message.from_user.id, f'Рассылка завершена, получили 4372/4736 юзеров. ✅')
        await state.finish()
    else:
        pass
    
@dp.callback_query_handler(text='get_test', state='*')
async def parser(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=True)
    try:
                                        
                            with connection.cursor() as cursor:
                                cursor.execute(f'SELECT * FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                row = cursor.fetchone()
    finally:            
                                        connection.close()
    if row[8] == 0:
        if row[2] != 0:
            await call.answer('Внимание ⚠\n\nУ вас уже есть активная подписка, если вы возьмете тестовую, то ваша подписка сменится на тестовую 3-х дневную подписку Light 💫', show_alert=True)
        else:
            kbtest = types.InlineKeyboardMarkup()
            kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
            imghello = types.InputMedia(type="photo", media=open('images/test.png', 'rb'), caption=f'Вам доступен бесплатный тестовый период длительностью в 3 дня ✅\n\nДля продолжения пришлите ссылку на ваш профиль Lolz.guru, к которому должен быть привязан текущий телеграм 📃')
            await call.message.edit_media(imghello, reply_markup=kbtest)
            await bot.send_message(5883902916, f'@{call.from_user.username} | ID: {call.from_user.id} пытается взять тестовую подписку 💎')
            await Test.next()
    else:
        await call.answer('Ошибка ❌\n\nВы уже брали тестовый период 😥', show_alert=True)
    
@dp.callback_query_handler(text='parse_settings', state='*')
async def parser(call: types.CallbackQuery, state: FSMContext):
    try:
                                        
                            with connection.cursor() as cursor:
                                cursor.execute(f'SELECT * FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                row = cursor.fetchone()
    finally:            
                                        connection.close()
    if str(row[2]) != '0':
        imghello = types.InputMedia(type="photo", media=open('images/settings.png', 'rb'), caption=f'Настройка парсера ⚙\n\nНиже представлены опции, которые вы можете изменить 🚀')
        await call.message.edit_media(imghello, reply_markup=kbsettings)
    else:
        call.answer('Доступ к этой возможности без активной подписки запрещен ❌', show_alert=True)
    
@dp.callback_query_handler(text='change_max_balance', state='*')
async def parser(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=True)
    await MaxBalance.next()
    try:
                                        
                            with connection.cursor() as cursor:
                                cursor.execute(f'SELECT * FROM parser_users WHERE id = %s', (call.from_user.id, ))
                                maxbal = int(cursor.fetchone()[10])
    finally:            
                                        connection.close()
    if maxbal == 9999999:
        maxbal = '∞'
    imghello = types.InputMedia(type="photo", media=open('images/settings.png', 'rb'), caption=f'🔗 Текущий максимальный баланс: {maxbal} $\n\n🤔 Пришлите желаемый максимальный баланс.')
    await call.message.edit_media(imghello, reply_markup=kbback)
    
@dp.message_handler(state=MaxBalance.maxbalance)
async def count(message: types.Message,  state: FSMContext):
    if message.text.isdigit():
            try:
                                        
                            with connection.cursor() as cursor:
                                cursor.execute('UPDATE parser_users SET maxbal = %s WHERE id = %s', (message.text, message.from_user.id))
                                connection.commit()
            finally:            
                connection.close()
            kbbackmain = types.InlineKeyboardMarkup()
            kbbackmain.add(types.InlineKeyboardButton(text='Вернуться в главное меню ✅', callback_data='back_to_main_menu2'))
            await bot.send_message(message.from_user.id, 'Максимальный баланс успешно установлен ✅', reply_markup=kbbackmain)
    else:
        await message.answer('Максимальный баланс должен быть написан цифрами')
    
@dp.message_handler(state=Test.lolz)
async def count(message: types.Message,  state: FSMContext):
    if 'zelenka.guru' in message.text or 'lolz.guru' in message.text or 'lolz.live' in message.text:
        try:
            connection = mysql.connector.connect(
            host=os.getenv('mysql_host'),
            user=os.getenv('mysql_username'),
            password=os.getenv('mysql_pass'),
            db=os.getenv('mysql_dbname'),
            charset='utf8mb4',
            connection_timeout=10000)                 
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT COUNT(*) FROM parser_users WHERE lolz = %s', (message.text, ))
                havelolz = cursor.fetchone()[0]
        finally:            
            connection.close()
        if havelolz != 0:
            try:
                    connection = mysql.connector.connect(
                                    host=os.getenv('mysql_host'),
                                    user=os.getenv('mysql_username'),
                                    password=os.getenv('mysql_pass'),
                                    db=os.getenv('mysql_dbname'),
                                    charset='utf8mb4',
                                    connection_timeout=10000)       
                    with connection.cursor() as cursor:
                                # connection is not autocommit by default. So you must commit to save
                        cursor.execute('INSERT INTO `blacklist`(`id`, `reason`) VALUES (%s,%s)', (message.from_user.id, 'Abuse'))
                        connection.commit()
            finally:            
                connection.close()
            await bot.send_message(message.from_user.id, f'⚠ Вам была выдана блокировка.\n\n📃 Причина: Abuse.')
            await bot.send_message(5883902916, f'@{message.from_user.username} | ID: {message.from_user.id} получил блокировку за Abuse 💎')
        else:
            headers = {'Authorization': 'Bearer a5a6b521a9705c26cbe6d8c34a80665559493c2c'}
            await message.answer('Ожидайте. Идет проверка... 🔎\n\nЕсли в течении 10 секунд не появится результат - попробуйте заново.')
            await asyncio.sleep(random.randint(4, 10))
            try:
                if '/members/' in message.text:
                    print(1228)
                    response = await async_http_get(f'https://api.zelenka.guru/users/{message.text.split("/")[4]}', headers=headers)
                    try:
                        timestamp = response['user']['user_register_date']
                        dt_object = datetime.datetime.fromtimestamp(timestamp)
                        current_date = datetime.datetime.now()
                        delta = current_date - dt_object
                        days = delta.days
                        if days < 30:
                            kbtest = types.InlineKeyboardMarkup()
                            kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                            await message.answer(f'Ошибка ❌\n\nНоворег форумник не пойдет, бро💎', reply_markup=kbtest)
                        else:
                            try:
                                resp = response['user']['fields'][16]['value'].upper()
                                #await bot.send_message(5883902916, f'ID: {message.from_userыыы.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @{resp} / TG: @{message.from_user.username}')
                                if resp == message.from_user.username.upper():
                                    print(1235)
                                    kbtest = types.InlineKeyboardMarkup()
                                    kbtest.add(types.InlineKeyboardButton(text= "Вернуться назад ✅", callback_data='private'))
                                    await bot.send_message(5883902916, f'@{message.from_user.username} | ID: {message.from_user.id} взял тест подписку 💎')
                                    await bot.send_photo(chat_id=message.from_user.id, photo=open('images/success.png', 'rb'), caption=f'Успешно ✅\n\nНа ваш аккаунт была зачислена Light 💫 подписка на 3 дня 💎\n\nУдачного ворка ⚡', reply_markup=kbtest)
                                    try:
                                            connection = mysql.connector.connect(
                                                            host=os.getenv('mysql_host'),
                                                            user=os.getenv('mysql_username'),
                                                            password=os.getenv('mysql_pass'),
                                                            db=os.getenv('mysql_dbname'),
                                                            charset='utf8mb4',
                                                            connection_timeout=10000)       
                                            with connection.cursor() as cursor:
                                                        
                                                a, b = datetime.datetime.now().strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"), datetime.timedelta(days = 3)
                                                cursor.execute('UPDATE parser_users SET plan = 1, billing_date =%s, limitstrings=%s, test = 1, lolz =%s WHERE id = %s', (a + b, 75, message.text, message.from_user.id))
                                                connection.commit()
                                    finally:            
                                        connection.close()
                                else:
                                    print(1256)
                                    kbtest = types.InlineKeyboardMarkup()
                                    kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                                    await bot.send_photo(chat_id=message.from_user.id, photo=open('images/lolztg.png', 'rb'), caption='Ошибка ❌\n\nТелеграм, который указан в контактах в профиле на лолзе не совпадает с текущим ⚠\n\nПопробуйте еще раз, отправив верную ссылку на Lolz, либо привязав телеграм к форуму🔗', reply_markup=kbtest)
                                    await asyncio.sleep(2)
                            except:
                                try:
                                    resp = response['user']['custom_fields']['telegram'].upper()
                                    if resp == message.from_user.username.upper():
                                        print(1265)
                                        kbtest = types.InlineKeyboardMarkup()
                                        kbtest.add(types.InlineKeyboardButton(text= "Вернуться назад ✅", callback_data='private'))
                                        await bot.send_message(5883902916, f'@{message.from_user.username} | ID: {message.from_user.id} взял тест подписку 💎')
                                        await bot.send_photo(chat_id=message.from_user.id, photo=open('images/success.png', 'rb'), caption=f'Успешно ✅\n\nНа ваш аккаунт была зачислена Light 💫 подписка на 3 дня 💎\n\nУдачного ворка ⚡', reply_markup=kbtest)
                                        try:
                                                connection = mysql.connector.connect(
                                                                host=os.getenv('mysql_host'),
                                                                user=os.getenv('mysql_username'),
                                                                password=os.getenv('mysql_pass'),
                                                                db=os.getenv('mysql_dbname'),
                                                                charset='utf8mb4',
                                                                connection_timeout=10000)       
                                                with connection.cursor() as cursor:
                                                            # connection is not autocommit by default. So you must commit to save
                                                    a, b = datetime.datetime.now().strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"), datetime.timedelta(days = 3)
                                                    cursor.execute('UPDATE parser_users SET plan = 1, billing_date =%s, limitstrings=%s, test = 1, lolz =%s WHERE id = %s', (a + b, 75, message.text, message.from_user.id))
                                                    connection.commit()
                                        finally:            
                                            connection.close()
                                    else:
                                        print(1286)
                                        kbtest = types.InlineKeyboardMarkup()
                                        kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                                        try:
                                            await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @{resp} / TG: @{message.from_user.username}')
                                        except:
                                            await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @None / TG: @{message.from_user.username}')
                                        await bot.send_photo(chat_id=message.from_user.id, photo=open('images/lolztg.png', 'rb'), caption='Ошибка ❌\n\nТелеграм, который указан в контактах в профиле на лолзе не совпадает с текущим ⚠\n\nПопробуйте еще раз, отправив верную ссылку на Lolz, либо привязав телеграм к форуму🔗', reply_markup=kbtest)
                                        await asyncio.sleep(2)
                                except:
                                    print(1293)
                                    kbtest = types.InlineKeyboardMarkup()
                                    kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                                    try:
                                        await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @{resp} / TG: @{message.from_user.username}')
                                    except:
                                        await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @None / TG: @{message.from_user.username}')
                                    await bot.send_photo(chat_id=message.from_user.id, photo=open('images/lolztg.png', 'rb'), caption='Ошибка ❌\n\nТелеграм, который указан в контактах в профиле на лолзе не совпадает с текущим ⚠\n\nПопробуйте еще раз, отправив верную ссылку на Lolz, либо привязав телеграм к форуму🔗', reply_markup=kbtest)
                                    await asyncio.sleep(2)      
                    except Exception as e:
                        traceback.print_exception
                        kbtest = types.InlineKeyboardMarkup()
                        kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                        await bot.send_photo(chat_id=message.from_user.id, photo=open('images/lolztg.png', 'rb'), caption=f'Ошибка ❌\n\nФорумник не найден 😅\n{e}', reply_markup=kbtest)
                        await asyncio.sleep(2)      
                else:
                    response = await async_http_get(f'https://api.zelenka.guru/users/{message.text.split("/")[3]}', headers=headers)
                    try:
                        timestamp = response['user']['user_register_date']
                        dt_object = datetime.datetime.fromtimestamp(timestamp)
                        current_date = datetime.datetime.now()
                        delta = current_date - dt_object
                        days = delta.days
                        if days < 30:
                            kbtest = types.InlineKeyboardMarkup()
                            kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                            await message.answer(f'Ошибка ❌\n\nНоворег форумник не пойдет, бро💎', reply_markup=kbtest)
                        else:
                            try:
                                resp = response['user']['custom_fields']['telegram'].upper()
                                if resp == message.from_user.username.upper():
                                    print(1304)
                                    kbtest = types.InlineKeyboardMarkup()
                                    kbtest.add(types.InlineKeyboardButton(text= "Вернуться назад ✅", callback_data='private'))
                                    await bot.send_message(5883902916, f'@{message.from_user.username} | ID: {message.from_user.id} взял тест подписку 💎')
                                    await bot.send_photo(chat_id=message.from_user.id, photo=open('images/success.png', 'rb'), caption=f'Успешно ✅\n\nНа ваш аккаунт была зачислена Light 💫 подписка на 3 дня 💎\n\nУдачного ворка ⚡', reply_markup=kbtest)
                                    try:
                                            connection = mysql.connector.connect(
                                                            host=os.getenv('mysql_host'),
                                                            user=os.getenv('mysql_username'),
                                                            password=os.getenv('mysql_pass'),
                                                            db=os.getenv('mysql_dbname'),
                                                            charset='utf8mb4',
                                                            connection_timeout=10000)       
                                            with connection.cursor() as cursor:
                                                        # connection is not autocommit by default. So you must commit to save
                                                a, b = datetime.datetime.now().strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"), datetime.timedelta(days = 3)
                                                cursor.execute('UPDATE parser_users SET plan = 1, billing_date =%s, limitstrings=%s, test = 1, lolz =%s WHERE id = %s', (a + b, 75, message.text, message.from_user.id))
                                                connection.commit()
                                    finally:            
                                        connection.close()
                                else:
                                    print(1325)
                                    kbtest = types.InlineKeyboardMarkup()
                                    kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                                    try:
                                        await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @{resp} / TG: @{message.from_user.username}')
                                    except:
                                        await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @None / TG: @{message.from_user.username}')
                                    await bot.send_photo(chat_id=message.from_user.id, photo=open('images/lolztg.png', 'rb'), caption='Ошибка ❌\n\nТелеграм, который указан в контактах в профиле на лолзе не совпадает с текущим ⚠\n\nПопробуйте еще раз, отправив верную ссылку на Lolz, либо привязав телеграм к форуму🔗', reply_markup=kbtest)
                                    await asyncio.sleep(2)
                            except:
                                try:
                                    resp = response['user']['fields'][16]['value'].upper()
                                    if resp == message.from_user.username.upper():
                                        print(1335)
                                        kbtest = types.InlineKeyboardMarkup()
                                        kbtest.add(types.InlineKeyboardButton(text= "Вернуться назад ✅", callback_data='private'))
                                        await bot.send_message(5883902916, f'@{message.from_user.username} | ID: {message.from_user.id} взял тест подписку 💎')
                                        await bot.send_photo(chat_id=message.from_user.id, photo=open('images/success.png', 'rb'), caption=f'Успешно ✅\n\nНа ваш аккаунт была зачислена Light 💫 подписка на 3 дня 💎\n\nУдачного ворка ⚡', reply_markup=kbtest)
                                        try:
                                                connection = mysql.connector.connect(
                                                                host=os.getenv('mysql_host'),
                                                                user=os.getenv('mysql_username'),
                                                                password=os.getenv('mysql_pass'),
                                                                db=os.getenv('mysql_dbname'),
                                                                charset='utf8mb4',
                                                                connection_timeout=10000)       
                                                with connection.cursor() as cursor:
                                                            # connection is not autocommit by default. So you must commit to save
                                                    a, b = datetime.datetime.now().strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"), datetime.timedelta(days = 3)
                                                    cursor.execute('UPDATE parser_users SET plan = 1, billing_date =%s, limitstrings=%s, test = 1, lolz =%s WHERE id = %s', (a + b, 75, message.text, message.from_user.id))
                                                    connection.commit()
                                        finally:            
                                            connection.close()
                                    else:
                                        print(1356)
                                        kbtest = types.InlineKeyboardMarkup()
                                        kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                                        try:
                                            await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @{resp} / TG: @{message.from_user.username}')
                                        except:
                                            await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @None / TG: @{message.from_user.username}')
                                        await bot.send_photo(chat_id=message.from_user.id, photo=open('images/lolztg.png', 'rb'), caption='Ошибка ❌\n\nТелеграм, который указан в контактах в профиле на лолзе не совпадает с текущим ⚠\n\nПопробуйте еще раз, отправив верную ссылку на Lolz, либо привязав телеграм к форуму🔗', reply_markup=kbtest)
                                        await asyncio.sleep(2)
                                except:
                                    print(1363)
                                    kbtest = types.InlineKeyboardMarkup()
                                    kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                                    try:
                                        await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @{resp} / TG: @{message.from_user.username}')
                                    except:
                                        await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @None / TG: @{message.from_user.username}')
                                    await bot.send_photo(chat_id=message.from_user.id, photo=open('images/lolztg.png', 'rb'), caption='Ошибка ❌\n\nТелеграм, который указан в контактах в профиле на лолзе не совпадает с текущим ⚠\n\nПопробуйте еще раз, отправив верную ссылку на Lolz, либо привязав телеграм к форуму🔗', reply_markup=kbtest)
                                    await asyncio.sleep(2)         
                    except Exception as e:
                        print(1370)
                        await bot.send_message(5883902916, f'ID: {message.from_user.id} не смог взять тест подписку ❌\n\nLolz: {message.text}\nLOLZ API: @None / TG: @{message.from_user.username}\n\n{e}')
            except Exception as e:
                        traceback.print_exception
                        kbtest = types.InlineKeyboardMarkup()
                        kbtest.add(types.InlineKeyboardButton(text= "Отмена ❌", callback_data='back_to_main_menu2'))
                        await bot.send_photo(chat_id=message.from_user.id, photo=open('images/lolztg.png', 'rb'), caption=f'Ошибка ❌\n\nФорумник не найден 😅\n{e}', reply_markup=kbtest)
                        await asyncio.sleep(2)      
    else:
        await message.answer('Это не ссылка на профиль Lolz ❌\n\nПопробуйте еще раз ⚡')