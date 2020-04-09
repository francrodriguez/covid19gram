#!/bin/env python
# -*- coding: utf-8 -*-
import string
import configparser
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import string
import time
import re
from collections import Counter
from time import sleep
from uuid import uuid4
import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plot
import pyrogram
import sys
import asyncio
from pyrogram import Client
from pyrogram import Filters, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InlineQueryResultPhoto,InputMediaPhoto, InputTextMessageContent, ReplyKeyboardMarkup
from pyrogram.api import functions as tg_api
from pyrogram.errors import FloodWait, BadRequest, RPCError
from covid19plot import COVID19Plot
from config.getdata import pull_datasets, pull_global
from config.countries import countries
from config.settings import DBHandler
from gettext import gettext as _
import gettext


config_file = "conf.ini"
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")

me = int(config["USER"]["admin"])
app = Client(
    "covid19bot",
    bot_token=config["API"]["api_token"],
    api_id=config["API"]["API_ID"],
    api_hash=config["API"]["API_HASH"]
)
cplt = COVID19Plot()
tot = cplt.get_global_regions()
world = cplt.get_global_regions()
comunitat= cplt.get_regions()
comunitat.sort()
tot.extend(comunitat)
tot.sort()

dbhd = DBHandler()


def normal(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("à", "a"),
        ("è", "e"),
        ("ï", "i"),
        ("ò", "o"),
        ("ü", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

def cerca(paraula,language = "en"):
    global tot
    cerca = normal(paraula).lower()
    resultats=[]
    for r in tot:
        if normal(r).lower().find(cerca)>-1:
            resultats.append(r)
    return resultats

def get_label(region ='Global', language = 'en'):
    if region in world:
        return '_(\n__Generated by [COVID19gram](t.me/COVID19gram_bot)__\n__Data source from [covid19.health](https://github.com/stevenliuyi/covid19/)__)'
    else:
        return '_(\n__Generated by [COVID19gram](t.me/COVID19gram_bot)__\n__Data source from [Datadista](https://github.com/datadista/datasets/)__)'


def get_img(region, dades="casos", language ="en"):
    filename = ""
    outfn = ""
    if dades == "casos":
        # filename = cplt.generate_daily_cases_img(region)
        filename = cplt.generate_plot(plot_type="daily_cases", region = region, language = language)
    elif dades == "tot":
    #     filename = cplt.generate_all_img(c_id)
        filename = cplt.generate_plot(plot_type="active_recovered_deceased", region = region, language = language)
    elif dades == "actius":
        # filename = cplt.generate_active_cases_img(c_id)
        filename = cplt.generate_plot(plot_type="active", region = region, language = language)
    elif dades == "altes":
        # filename = cplt.generate_altes_img(c_id)
        filename = cplt.generate_plot(plot_type="recovered", region = region, language = language)
    elif dades == "def":
        # filename = cplt.generate_defuncions_img(c_id)
        filename = cplt.generate_plot(plot_type="daily_deceased", region = region, language = language)
    return filename

def get_caption(c_id,dades="casos",language="en"):
    flag = ""
    if c_id in countries:
        flag = countries[c_id]['flag']
    region = flag + c_id
    if dades == "casos":
        return _('Active cases at {region}').format(region=_(region))
    elif dades == "tot":
        return _('Active cases, recovered and deceased at {region}').format(region=_(region))
    elif dades == "actius":
        return _('Active cases at {region}').format(region=_(region))
    elif dades == "altes":
        return _('Recovered cases at {region}').format(region=_(region))
    elif dades == "def":
        return _('Deaths evolution at {region}').format(region=_(region))

def botons(taula,dades="casos",regio="Total",font="spain",language="en"):
    ibt=[]
    l_botns =[]
    botonets = []
    result_all = []
    len_all = 0
    for chart in list(string.ascii_lowercase):
        result = [i for i in taula if i[0].lower()==(chart)]
        result_all.extend(result)
        if len(result_all)>7 or chart == "z":
            len_all = 0
            for item in result_all:
                flag = ""
                if item in countries:
                    flag = countries[item]['flag']
                ibt.append(InlineKeyboardButton(flag+item,callback_data=item+"_"+dades))
            botonets = [ibt[i*3 : (i+1)*3] for i in range((len(ibt)//4)+2)]
            botonets.extend([[InlineKeyboardButton(_("⬅️Back"),callback_data="back_"+font)]])
            btns = InlineKeyboardMarkup(botonets)
            l_botns.append(btns)
            ibt=[]
            botonets = []
            result_all = []
    return l_botns

def b_alphabet(taula,dades="casos",regio="Total", font="spain",language="en"):
    ibt=[]
    botonets = []
    ordre = 0
    text = ""
    len_all = 0
    s_char = ""
    for chart in list(string.ascii_lowercase):
        result = [i for i in taula if i[0].lower()==(chart)]
        len_all += len(result)
        if len_all>7 or chart == "z":
            if s_char =="":
                text = chart.upper()
            else:
                text = s_char +"-"+chart.upper()
            s_char = ""
            len_all = 0
            ibt.append(InlineKeyboardButton(text,callback_data="alph_"+str(ordre)+"_"+font))
            ordre +=1
        elif len(result)>0:
            if s_char =="":
                s_char = chart.upper()
    botonets = [ibt[i*3 : (i+1)*3] for i in range((len(ibt)//4)+2)]
    btns = InlineKeyboardMarkup(botonets)
    return btns

def b_single(dades="casos",regio="Total",language="en"):
    ibt=[]
    botonets = [[InlineKeyboardButton("🦠",callback_data="s_"+regio+"_casos"),InlineKeyboardButton("📊",callback_data="s_"+regio+"_tot"),InlineKeyboardButton("📈",callback_data="s_"+regio+"_actius"),InlineKeyboardButton("✅",callback_data="s_"+regio+"_altes"),InlineKeyboardButton("❌",callback_data="s_"+regio+"_def")]]
    btns = InlineKeyboardMarkup(botonets)
    return btns

def b_find(search,dades="casos",language="en"):
    taula = cerca(search)
    ibt = []
    l_botns =[]
    botonets = []
    pageSize = 18
    max = len(taula)//pageSize
    if len(taula)%pageSize != 0:
        max = len(taula)//pageSize + 1

    for pag in range(max):
        for item in taula[pag*pageSize : (pag+1)*pageSize]:
            flag = ""
            if item in countries:
                flag = countries[item]['flag']
            ibt.append(InlineKeyboardButton(flag+item,callback_data=item+"_"+dades))
        botonets = [ibt[i*3 : (i+1)*3] for i in range((len(ibt)//4)+2)]
        if pag == 0 and pag != max-1:
            botonets.extend([[InlineKeyboardButton(">>",callback_data="f_"+str(pag+1)+"_"+search)]])
        elif pag == max-1 and pag != 0:
            botonets.extend([[InlineKeyboardButton("<<",callback_data="f_"+str(pag-1)+"_"+search)]])
        elif pag >0 and pag < max-1:
            botonets.extend([[InlineKeyboardButton("<<",callback_data="f_"+str(pag-1)+"_"+search),InlineKeyboardButton(">>",callback_data="f_"+str(pag+1)+"_"+search)]])
        btns = InlineKeyboardMarkup(botonets)
        l_botns.append(btns)
        ibt=[]
        botonets = []

    return l_botns

def b_spain(taula,dades="casos",language="en"):
    ibt = []
    l_botns =[]
    botonets = []
    for item in taula:
        ibt.append(InlineKeyboardButton(item,callback_data=item+"_"+dades))
    botonets = [ibt[i*3 : (i+1)*3] for i in range((len(ibt)//4)+2)]
    btns = InlineKeyboardMarkup(botonets)
    l_botns.append(btns)
    return l_botns[0]

def b_lang(language="en"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("English",callback_data="lang_en"),InlineKeyboardButton("Català",callback_data="lang_ca"),InlineKeyboardButton("Español",callback_data="lang_es")]])

def b_start(language="en"):
    rep_markup = ReplyKeyboardMarkup([
            [_("🌐Global"),_("🇪🇸Spain")],[_("💬Language"),_("❓help")] # row 1
            ],
            resize_keyboard = True
            )
    return rep_markup

async def set_language(user_id, language):
        await dbhd.set_language(user_id, language)

async def get_language(user):
    user_id = user.id
    language = await dbhd.get_language(user_id)
    if  language != 'None':
        return language
    elif user.language_code and user.language_code in cplt.LANGUAGES:
        return user.language_code
    else:
        return 'en'

async def show_region(client, chat, dataSource = "casos",region = "Total", language = 'en'):
    btns = b_single(dades=dataSource,regio=region)
    flname = get_img(region,dataSource, language = language)
    caption = get_caption(region,dataSource, language = language)+get_label(region, language = language)
    try:
        await client.send_photo(chat, photo=flname, caption = caption, reply_markup=btns)
    except BadRequest as e:
        if str(e).find("IMAGE_PROCESS_FAILED")>-1:
            os.remove(flname)
            flname = get_img(region,dataSource, language = language)
            await client.send_photo(chat, photo=flname, caption = caption, reply_markup=btns)
        elif str(e).find("MESSAGE_NOT_MODIFIED")>-1:
            print("Error: "+str(e))
    except:
        print("Unexpected error:")
        raise

async def edit_region(client, chat, mid, dataSource = "casos",region = "Total", language = "en"):
    btns = b_single(dades=dataSource,regio=region, language = language)
    flname = get_img(region,dataSource, language = language)
    caption = get_caption(region,dataSource, language = language)+get_label(region, language = language)
    try:
        await client.edit_message_media(chat,mid,InputMediaPhoto(media=flname,caption = caption),reply_markup=btns)
    except BadRequest as e:
        if str(e).find("IMAGE_PROCESS_FAILED")>-1:
            os.remove(flname)
            flname = get_img(region,dataSource, language = language)
            await client.edit_message_media(chat,mid,InputMediaPhoto(media=flname,caption = caption),reply_markup=btns)
        elif str(e).find("MESSAGE_NOT_MODIFIED")>-1:
            print("Error: "+str(e))
    except:
        print("Unexpected error:")
        raise

async def DoBot(comm, param, client, message, language = "en",**kwargs):
    global config_file
    global config
    global me
    global comunitat
    user = message.from_user.id
    chat = message.chat.id
    if comm == "start":
        btns = b_alphabet(comunitat)
        rep_markup = b_start()
        await client.send_message(chat, _("⚙️Main Menu"),   reply_markup=rep_markup)
    if comm == "spain":
        btns = b_spain(comunitat)
        caption = "Choose a Region"
        await client.send_message(chat, _("Choose a Region"),   reply_markup=btns)
    if comm == "world":
        btns = b_alphabet(world,font="world")
        caption = "Choose a Region"
        await client.send_message(chat, _("Choose a Region"),   reply_markup=btns)
    elif comm == "clean" and user == me:
        filelist = [ f for f in os.listdir("images") if f.endswith(".png") ]
        for f in filelist:
            os.remove(os.path.join("images", f))
        filelist = [ f for f in os.listdir("mimages") if f.endswith(".png") ]
        for f in filelist:
            os.remove(os.path.join("mimages", f))
    elif comm == "find":
        if len(param)>0:
            resultats = cerca(param)
            if len(resultats) == 0:
                await client.send_message(chat, _('No results for `{param}`').format(param=param))
            elif len(resultats) == 1:
                await show_region(client, chat, region =
                                  resultats[0])
            else:
                btns = b_find(param)[0]
                caption = f'Search Results for `{param}`'
                await client.send_message(chat, caption,   reply_markup=btns)




@app.on_message(Filters.text)
async def g_request(client, message):
    global config_file
    global config
    global me
    global comunitat
    user = message.from_user.id
    chat = message.chat.id
    language = await get_language(message.from_user)
    if message.text.startswith('/'):
        comm = message.text.split()[0].strip('/')
        param = ""
        if re.match ('^/' + comm + ' .+$', message.text):
            param = re.search('^/' + comm + ' (.+)$', message.text).group(1)
        await DoBot(comm, param, client, message,language)
    elif message.text == _("🌐Global"):
        await DoBot("world", "", client, message,language)
    elif message.text == _("🇪🇸Spain"):
        await DoBot("spain", "", client, message,language)
    elif message.text == _("💬Language"):
        btns= b_lang(language)
        await client.send_message(chat, _("Choose Language"), reply_markup=btns)
    else:
        param = message.text
        resultats = cerca(param, language)
        if len(resultats) == 0:
            await client.send_message(chat, _('No results for `{param}`').format(param=param))
        elif len(resultats) == 1:
            await show_region(client, chat, region = resultats[0], language = language)
        else:
            btns = b_find(param)[0]
            caption =  _('Search results for `{param}`').format(param=param)
            await client.send_message(chat, caption,   reply_markup=btns)


@app.on_callback_query()
async def answer(client, callback_query):
    global comunitat
    cbdata = callback_query.data
    user = callback_query.from_user
    chat = callback_query.message.chat.id
    mid = callback_query.message.message_id
    params = callback_query.data.split("_")
    comm = params[0]
    language = await get_language(user)
    if comm == "pag":
        pag = int(params[1])
        btns = botons(comunitat)[pag]
        caption = _("Choose a Region")
        await client.edit_message_text(chat,mid,caption,reply_markup=btns)

    elif comm == "back":
        font = params[1]
        if font == "world":
            btns = b_alphabet(world,font="world", language = language)
        else:
            btns = b_alphabet(comunitat, language = language)
        text = _("Choose a Region")
        await client.edit_message_text(chat,mid, text, reply_markup=btns)

    elif comm == "s":
        region = params[1]
        dataSource = params[2]
        flname =""
        if region in tot:
            await edit_region(client, chat, mid, dataSource,region, language = language)

    if comm == "lang":
        language = params[1]
        await set_language(user.id, language)
        await client.send_message(chat, _("Your language is now English"))

    elif comm == "alph":
        pag = int(params[1])
        font = params[2]
        btns = []
        if font == "world":
            btns = botons(world,font="world", language = language)[pag]
        else:
            btns = botons(comunitat, language = language)[pag]
        caption = _("Choose a Region")
        await client.edit_message_text(chat,mid,caption,reply_markup=btns)

    elif comm == "f":
        pag = int(params[1])
        param = params[2]
        btns = b_find(param, language = language)[pag]
        caption = _('Search results for `{param}`').format(param=param)
        await client.edit_message_text(chat, mid, caption, reply_markup=btns)

    elif comm in tot:
        region = comm
        dataSource = params[1]
        await show_region(client, chat, dataSource,region, language = language)


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(pull_datasets, "interval", hours=1)
    scheduler.add_job(pull_global, "interval", hours=1)
    scheduler.start()
    await app.start()
    print("Started")
    await app.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


