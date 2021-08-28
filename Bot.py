import discord
from discord.ext import commands
import asyncio
from discord.utils import get
import youtube_dl
import requests
from PIL import Image, ImageFont, ImageDraw
import io
import json
import sqlite3
import os
import random
from random import randint
from discord_components import DiscordComponents, Button, ButtonStyle

client = commands.Bot( command_prefix = '>' )
client.remove_command('help')

hello_words = ['hello', 'hi', 'привет', 'салют', 'прив', 'хай']
answer_words = ['инфа о боте']

bad_words = ['херня', 'хер']

queue = []

list_it_us = []

list_it_us1 = []

events_queue = []

top = []

@client.command()
async def daily(ctx):
    with open('economy.json', 'r') as f:
        money = json.load(f)

    if not str(ctx.author.id) in money:
        money[str(ctx.author.id)] = {}
        money[str(ctx.author.id)]['Money'] = 0
        money[str(ctx.author.id)]['Money']['Nickname'] = f'{ctx.author}'

    if not str(ctx.author.id) in queue:
        emb = discord.Embed(description = f'**{ctx.author.mention}**, вы получили 50:money_with_wings:')
        await ctx.send(embed = emb)
        money[str(ctx.author.id)]['Money'] += 50
        queue.append(str(ctx.author.id))
        with open('economy.json', 'w') as f:
            json.dump(money, f)
        await asyncio.sleep(4 * 3600)
        queue.remove(str(ctx.author.id))

    if str(ctx.author.id) in queue:
        emb = discord.Embed(description = f'**{ctx.author.mention}**, вы уже получили награду!')
        await ctx.send(embed = emb)

@client.command()
async def bal(ctx, member:discord.Member = None):
    if member == ctx.author or member == None:
        with open('economy.json', 'r') as f:
            money = json.load(f)
            emb = discord.Embed(description=f'Баланс **{ctx.author.mention}**: {money[str(ctx.author.id)]["Money"]}:money_with_wings:')
        await ctx.send(embed = emb)
    else:
        with open('economy.json','r') as f:
            money = json.load(f)
        emb = discord.Embed(description=f'Баланс **{member.mention}**: {money[str(member.id)]["Money"]} :money_with_wings:')
        await ctx.send(embed = emb)


@client.command()
@commands.has_permissions(administrator = True)
async def addrole(ctx, role:discord.Role, cost:int):
    with open('economy.json','r') as f:
        money = json.load(f)
    if str(role.id) in money['shop']:
        await ctx.send("Эта роль уже есть в магазине!")
    if not str(role.id) in money['shop']:
        money['shop'][str(role.id)] ={}
        money['shop'][str(role.id)]['Cost'] = cost
        emb = discord.Embed(description = 'Роль успешно добавлена в магазин!', colour = discord.Color.green())
        await ctx.send(embed = emb)
    with open('economy.json','w') as f:
        json.dump(money,f)


@client.command()
async def shop(ctx):
    await ctx.channel.purge(limit = 1)
    with open('economy.json','r') as f:
        money = json.load(f)
    emb = discord.Embed(title = '===Магазин===', colour = discord.Color.green())
    for role in money['shop']:
        emb.add_field(name = f'Цена: {money["shop"][role]["Cost"]}:money_with_wings:', value = f'<@&{role}>', inline = False)
    await ctx.send(embed = emb)


@client.command()
@commands.has_permissions(administrator = True)
async def delrole(ctx, role:discord.Role):
    with open('economy.json','r') as f:
        money = json.load(f)

    if not str(role.id) in money['shop']:
        emb = discord.Embed(description = 'Этой роли нет в магазине!', colour = discord.Color.red())
        await ctx.send(embed = emb)
    if str(role.id) in money['shop']:
        emb = discord.Embed(description = 'Роль успешно удалена из магазина!', colour = discord.Color.green())
        await ctx.send(embed = emb)
        del money['shop'][str(role.id)]
    with open('economy.json','w') as f:
        json.dump(money,f)


@client.command()
async def buy(ctx, role:discord.Role):
    with open('economy.json','r') as f:
        money = json.load(f)
    if str(role.id) in money['shop']:
        if money['shop'][str(role.id)]['Cost'] <= money[str(ctx.author.id)]['Money']:
            if not role in ctx.author.roles:
                emb = discord.Embed(description = 'Вы купили роль!', colour = discord.Color.green())
                await ctx.send(embed = emb)
                for i in money['shop']:
                    if i == str(role.id):
                        buy = discord.utils.get(ctx.guild.roles, id = int(i))
                        await ctx.author.add_roles(buy)
                        money[str(ctx.author.id)]['Money'] -= money['shop'][str(role.id)]['Cost']
            else:
                emb = discord.Embed(description = 'У вас уже есть эта роль!', colour = discord.Color.red())
                await ctx.send(embed = emb)

    with open('economy.json','w') as f:
        json.dump(money, f)


@client.command()
async def give(ctx, member:discord.Member, arg:int):
    with open('economy.json','r') as f:
        money = json.load(f)
    if not str(ctx.author.id) in money:
        money[str(ctx.author.id)] = {}
        money[str(ctx.author.id)]['Money'] = 0

        emb = discord.Embed(title = 'Ошибка!', colour = discord.Color.red())
        emb.add_field(name = 'У вас или у получителя не было кошелька, но я уже все сделал'.format(ctx), value = 'Попробуйте ещё раз', inline = False)
        await ctx.send(embed = emb)
    if money[str(ctx.author.id)]['Money'] >= arg:
        emb = discord.Embed(description = f'{ctx.author.mention} перевёл {member} {arg}:money_with_wings:', colour = discord.Color.green())
        money[str(ctx.author.id)]['Money'] -= arg
        money[str(member.id)]['Money'] += arg
        await ctx.send(embed = emb)
    else:
        emb = discord.Embed(description = 'Не хватает :money_with_wings: для перевода!', colour = discord.Color.red())
        await ctx.send(embed = emb)
    with open('economy.json','w') as f:
        json.dump(money, f)


@client.command()
async def game(ctx, arg:int):
    with open('economy.json','r') as f:
        money = json.load(f)
    botsc = randint(1, 10)
    if arg > 10:
        emb = discord.Embed(title = 'Игра', colour = discord.Color.green())
        emb.add_field(name = 'Число игрока:'.format(arg), value = f'{arg}', inline = False)
    if arg > botsc:
        emb = discord.Embed(title = 'Игра', colour = discord.Color.green())
        emb.add_field(name = 'Число игрока:'.format(arg), value = f'{arg}', inline = False)
        emb.add_field(name = 'Число бота:'.format(arg), value = f'{botsc}', inline = False)
        emb.add_field(name = 'Победитель:'.format(ctx), value = f'{ctx.author.mention}', inline = False)
        emb.add_field(name = 'Выигрыш:'.format(ctx), value = '100:money_with_wings:', inline = False)
        money[str(ctx.author.id)]['Money'] += 100
        await ctx.send(embed = emb)
    if arg < botsc:
        emb = discord.Embed(title = 'Игра', colour = discord.Color.green())
        emb.add_field(name = 'Число игрока:'.format(arg), value = f'{arg}', inline = False)
        emb.add_field(name = 'Число бота:'.format(arg), value = f'{botsc}', inline = False)
        emb.add_field(name = 'Победитель:'.format(ctx), value = 'Бот', inline = False)
        emb.add_field(name = 'Проигрыш:'.format(ctx), value = '100:money_with_wings:', inline = False)
        money[str(ctx.author.id)]['Money'] -= 100
        await ctx.send(embed = emb)
    if arg == botsc:
        emb = discord.Embed(title = 'Игра', colour = discord.Color.green())
        emb.add_field(name = 'Число игрока:'.format(arg), value = f'{arg}', inline = False)
        emb.add_field(name = 'Число бота:'.format(arg), value = f'{botsc}', inline = False)
        emb.add_field(name = 'Победитель:'.format(ctx), value = 'Ничья!', inline = False)
        emb.add_field(name = 'Выигрыш:'.format(ctx), value = '0', inline = False)
        await ctx.send(embed = emb)
    with open('economy.json','w') as f:
        json.dump(money, f)


@client.command()
async def random(ctx, arg:int):
    with open('economy.json','r') as f:
        money = json.load(f)
    botsc = randint(1, 100)
    usrsc = randint(1, 100)
    if usrsc > botsc:
        emb = discord.Embed(title = 'Рандом', colour = discord.Color.green())
        emb.add_field(name = 'Число игрока:'.format(arg), value = f'{usrsc}', inline = False)
        emb.add_field(name = 'Число бота:'.format(arg), value = f'{botsc}', inline = False)
        emb.add_field(name = 'Победитель:'.format(ctx), value = f'{ctx.author.mention}', inline = False)
        emb.add_field(name = 'Ставка:'.format(ctx), value = f'{arg}:money_with_wings:', inline = False)
        money[str(ctx.author.id)]['Money'] += arg
        await ctx.send(embed = emb)
    if usrsc < botsc:
        emb = discord.Embed(title = 'Рандом', colour = discord.Color.green())
        emb.add_field(name = 'Число игрока:'.format(arg), value = f'{usrsc}', inline = False)
        emb.add_field(name = 'Число бота:'.format(arg), value = f'{botsc}', inline = False)
        emb.add_field(name = 'Победитель:'.format(ctx), value = 'Бот', inline = False)
        emb.add_field(name = 'Ставка:'.format(ctx), value = f'{arg}:money_with_wings:', inline = False)
        money[str(ctx.author.id)]['Money'] -= arg
        await ctx.send(embed = emb)
    if usrsc == botsc:
        emb = discord.Embed(title = 'Рандом', colour = discord.Color.green())
        emb.add_field(name = 'Число игрока:'.format(arg), value = f'{usrsc}', inline = False)
        emb.add_field(name = 'Число бота:'.format(arg), value = f'{botsc}', inline = False)
        emb.add_field(name = 'Победитель:'.format(ctx), value = 'Ничья!', inline = False)
        emb.add_field(name = 'Ставка'.format(ctx), value = '0', inline = False)
        await ctx.send(embed = emb)
    with open('economy.json','w') as f:
        json.dump(money, f)


@client.command()
async def jobs(ctx):
    emb = discord.Embed(title = 'Устроиться на работу', colour = discord.Color.green())
    emb.add_field(name = 'Дворник(нужен 3 уровень)'.format(ctx), value = 'ЗП: 10:money_with_wings:', inline = False)
    await ctx.send(embed = emb)


@client.command()
async def job(ctx):
    with open('lvl.json','r') as f:
        users = json.load(f)
    if users[str(ctx.author.id)]['lvl'] >= 3:
        dv_role = discord.utils.get(ctx.message.guild.roles, name = 'Дворник')

        await ctx.author.add_roles( dv_role )

        emb = discord.Embed(description = f'Теперь {ctx.author.mention} работает дворником! ', colour = discord.Color.green())
        await ctx.send(embed = emb)
    else:
        emb = discord.Embed(description = 'Не хватает уровня для принятия на работу!', colour = discord.Color.red())
        await ctx.send(embed = emb)


@client.command()
async def zp(ctx):
    with open('economy.json','r') as f:
        money = json.load(f)

    dv_role = discord.utils.get(ctx.message.guild.roles, name = 'Дворник')

    if dv_role in ctx.author.roles:
        if not str(ctx.author.id) in queue:
            emb = discord.Embed(description = f'**{ctx.author.mention}**, вы получили 10:money_with_wings:')
            await ctx.send(embed = emb)
            money[str(ctx.author.id)]['Money'] += 10
            queue.append(str(ctx.author.id))
            await asyncio.sleep(4 * 3600)
            queue.remove(str(ctx.author.id))

        if str(ctx.author.id) in queue:
            emb = discord.Embed(description = f'**{ctx.author.mention}**, вы уже получили зарплату!')
            await ctx.send(embed = emb)

    with open('economy.json','w') as f:
        json.dump(money, f)


@client.command()
async def sitems(ctx):
    emb = discord.Embed(title = '===Магазин предметов===', colour = discord.Color.green())

    emb.add_field(name = 'Удочка(1) -- 200:money_with_wings:'.format(ctx), value = 'Позволяет ловить рыбу', inline = False)
    emb.add_field(name = 'Кирка(2) -- 350:money_with_wings:'.format(ctx), value = 'Позволяет копать руду в шахте', inline = False)

    await ctx.send(embed = emb)


@client.command()
async def buy_item1(ctx):
    with open('economy.json','r') as f:
        money = json.load(f)

    if money[str(ctx.author.id)]["Money"] >= 200:
        emb = discord.Embed(title = 'Удочка', colour = discord.Color.green())

        emb.add_field(name = 'Покупка совершена:'.format(ctx), value = 'Вы успешно купили удочку!')

        await ctx.send(embed = emb)

        money[str(ctx.author.id)]["Money"] -= 200

        list_it_us.append(str(ctx.author.id))
    else:
        emb = discord.Embed(description = 'Не хватает :money_with_wings: для покупки!', colour = discord.Color.red())

        await ctx.send(embed = emb)


    with open('economy.json','w') as f:
        json.dump(money, f)


@client.command()
async def buy_item2(ctx):
    with open('economy.json','r') as f:
        money = json.load(f)

    if money[str(ctx.author.id)]["Money"] >= 300:
        emb = discord.Embed(title = 'Кирка', colour = discord.Color.green())

        emb.add_field(name = 'Покупка совершена:'.format(ctx), value = 'Вы успешно купили кирку!')

        await ctx.send(embed = emb)

        money[str(ctx.author.id)]["Money"] -= 300
        list_it_us1.append(str(ctx.author.id))

    if money[str(ctx.author.id)]["Money"] < 300:
        emb = discord.Embed(description = 'Не хватает :money_with_wings: для покупки!', colour = discord.Color.red())

        await ctx.send(embed = emb)


    with open('economy.json','w') as f:
        json.dump(money, f)


@client.command()
@commands.has_permissions(administrator = True)
async def get(ctx, arg:int):
    with open('economy.json', 'r') as f:
        money = json.load(f)

        money[str(ctx.author.id)]["Money"] += arg

        await ctx.send('Бабло успешно накручено')

    with open('economy.json', 'w') as f:
        json.dump(money, f)

@client.command()
async def duel(ctx, member:discord.Member, bet:int):
    await ctx.channel.purge(limit = 1)
    with open('economy.json', 'r') as f:
        money = json.load(f)

        if member == ctx.author or member == None:
            emb = discord.Embed(description = 'Ошибка! Нет соперника для дуэли', colour = discord.Color.red())
            await ctx.send(embed = emb)
        if bet <= 0 or bet == None:
            emb = discord.Embed(description = 'Ошибка! Не указана ставка для дуэли', colour = discord.Color.red())
            await ctx.send(embed = emb)
        if money[str(ctx.author.id)]['Money'] < bet or money[str(member.id)]['Money'] < bet:
            emb = discord.Embed(description = 'Ошибка! Недостаточно денег для дуэли', colour = discord.Color.red())
            await ctx.send(embed = emb)
        else:
            emb = discord.Embed(title = 'Дуэль', colour = discord.Color.green())
            emb.add_field(name = f'Пользователь {ctx.author} вызвал вас на дуэль'.format(member), value = 'У вас есть 30 секунд, чтобы принять дуэль')
            emb.set_author(name = 'Отправитель', icon_url = ctx.author.avatar_url)
            emb.set_footer(text = 'Соперник', icon_url = member.avatar_url)
            await ctx.send(
                embed = emb,
                components=[
                    Button(style=ButtonStyle.green, label="Принять"),
                    Button(style=ButtonStyle.red, label="Отклонить")
                ]
            )

            response = await client.wait_for("button_click")
            if response.channel == ctx.channel:
                if response.component.label == "Принять":
                    reska = randint(1,2)

                    if reska == 1:
                        await response.respond(embed = discord.Embed(description = f"Победил {ctx.author.mention}!", colour = discord.Color.green()))
                        await ctx.channel.purge(limit = 1)
                        money[str(ctx.author.id)]["Money"] += bet
                        money[str(member.id)]["Money"] -= bet
                    if reska == 2:
                        await response.respond(embed = discord.Embed(description = f"Победил {member.mention}!", colour = discord.Color.green()))
                        await ctx.channel.purge(limit = 1)
                        money[str(ctx.author.id)]["Money"] -= bet
                        money[str(member.id)]["Money"] += bet
                if response.component.label == "Отклонить":
                    await response.respond(embed = discord.Embed(description = f'{member.mention} отказался от дуэли'))



            await asyncio.sleep(30)
            await ctx.channel.purge(limit = 1)
            emb = discord.Embed(description = f'Время вышло!')
            await ctx.send(embed = emb)

    with open('economy.json', 'w') as f:
        json.dump(money, f)


@client.command()
async def lb(ctx):
    with open('economy.json', 'r') as f:
        money = json.load(f)

        emb = discord.Embed(title = 'Топ 10 богачей сервера')
        counter = 0

        for i in money:
            counter += 1
            emb.add_field(name = f'{counter} {money[str(ctx.author.id)]}', value = f'Баланс: {money[str(ctx.author.id)]["Money"]}', inline = False)

        await ctx.send(embed = emb)




@client.command()
async def open1(ctx, member:discord.Member):
    role1 = discord.utils.get(ctx.message.guild.roles, name = 'Доступ в 1 комнату')
    if not role1 in ctx.author.roles:
        emb = discord.Embed(description=f'У вас нет прав на эту комнату!')
        await ctx.send(embed = emb)
    if member == ctx.author or member == None:
        emb = discord.Embed(description=f'Ты не указал пользователя!')
        await ctx.send(embed = emb)
    if role1 not in member.roles:
        await member.add_roles(role1)

        emb = discord.Embed(description=f'Теперь{member.mention} имеет доступ к 1 комнате')
        await ctx.send(embed = emb)
    if role1 in member.roles:
        emb = discord.Embed(description=f'Этот пользователь уже имеет доступ к комнате!')
        await ctx.send(embed = emb)


@client.command()
async def close1(ctx, member:discord.Member):
    role1 = discord.utils.get(ctx.message.guild.roles, name = 'Доступ в 1 комнату')
    if member == ctx.author or member == None:
        emb = discord.Embed(description=f'Ты не указал пользователя!')
        await ctx.send(embed = emb)
    if role1 not in member.roles:

        emb = discord.Embed(description=f'У {member.mention} уже нет доступа!')
        await ctx.send(embed = emb)
    if role1 in member.roles:
        await member.remove_roles(role1)

        emb = discord.Embed(description=f'Теперь {member.mention} не имеет доступа к этой комнате')
        await ctx.send(embed = emb)


@client.command()
async def open2(ctx, member:discord.Member):
    role2 = discord.utils.get(ctx.message.guild.roles, name = 'Доступ во 2 комнату')
    if not role2 in ctx.author.roles:
        emb = discord.Embed(description=f'У вас нет прав на эту комнату!')
        await ctx.send(embed = emb)
    if member == ctx.author or member == None:
        emb = discord.Embed(description=f'Ты не указал пользователя!')
        await ctx.send(embed = emb)
    if role2 not in member.roles:
        await member.add_roles(role1)

        emb = discord.Embed(description=f'Теперь{member.mention} имеет доступ ко 2 комнате')
        await ctx.send(embed = emb)
    if role2 in member.roles:
        emb = discord.Embed(description=f'Этот пользователь уже имеет доступ к комнате!')
        await ctx.send(embed = emb)


@client.command()
async def close2(ctx, member:discord.Member):
    role2 = discord.utils.get(ctx.message.guild.roles, name = 'Доступ в 1 комнату')
    if not role2 in ctx.author.roles:
        emb = discord.Embed(description=f'У вас нет прав на эту комнату!')
        await ctx.send(embed = emb)
    if member == ctx.author or member == None:
        emb = discord.Embed(description=f'Ты не указал пользователя!')
        await ctx.send(embed = emb)
    if role2 not in member.roles:
        emb = discord.Embed(description=f'У {member.mention} уже нет доступа!')
        await ctx.send(embed = emb)
    if role2 in member.roles:
        await member.remove_roles(role1)

        emb = discord.Embed(description=f'Теперь {member.mention} не имеет доступа к этой комнате')
        await ctx.send(embed = emb)


@client.command()
async def open3(ctx, member:discord.Member):
    role2 = discord.utils.get(ctx.message.guild.roles, name = 'Доступ во 2 комнату')
    if not role2 in ctx.author.roles:
        emb = discord.Embed(description=f'У вас нет прав на эту комнату!')
        await ctx.send(embed = emb)
    if member == ctx.author or member == None:
        emb = discord.Embed(description=f'Ты не указал пользователя!')
        await ctx.send(embed = emb)
    if role2 not in member.roles:
        await member.add_roles(role1)

        emb = discord.Embed(description=f'Теперь{member.mention} имеет доступ ко 2 комнате')
        await ctx.send(embed = emb)
    if role2 in member.roles:
        emb = discord.Embed(description=f'Этот пользователь уже имеет доступ к комнате!')
        await ctx.send(embed = emb)


@client.command()
async def close3(ctx, member:discord.Member):
    role3 = discord.utils.get(ctx.message.guild.roles, name = 'Доступ в 3 комнату')
    if not role3 in ctx.author.roles:
        emb = discord.Embed(description=f'У вас нет прав на эту комнату!')
        await ctx.send(embed = emb)
    if member == ctx.author or member == None:
        emb = discord.Embed(description=f'Ты не указал пользователя!')
        await ctx.send(embed = emb)
    if role3 not in member.roles:
        emb = discord.Embed(description=f'У {member.mention} уже нет доступа!')
        await ctx.send(embed = emb)
    if role3 in member.roles:
        await member.remove_roles(role1)

        emb = discord.Embed(description=f'Теперь {member.mention} не имеет доступа к этой комнате')
        await ctx.send(embed = emb)



@client.command()
async def roulette(ctx, arg:int):
    with open('economy.json','r') as f:
        money = json.load(f)

    if arg > 50:
        money[str(ctx.author.id)]["Money"] -= arg
        emb = discord.Embed(title = '🎰Рулетка🎰', colour = discord.Color.green())
        emb.add_field(name = 'Крутится рулетка...'.format(ctx), value = 'Через 10 секунд будет результат')
        message = await ctx.send(embed = emb)

        await asyncio.sleep(10)
        win_sum = randint(1, arg * 2)
        await message.edit(content = f'Вы получаете: {win_sum}:money_with_wings:')
        money[str(ctx.author.id)]["Money"] += win_sum
    if arg < 50:
        emb = discord.Embed(title = 'Ошибка!', colour = discord.Color.red())
        emb.add_field(name = 'Неправильная ставка'.format(ctx), value = 'Минимальная ставка 50:money_with_wings:')
        await ctx.send(embed = emb)

    with open('economy.json', 'w') as f:
        json.dump(money, f)


@client.command()
@commands.has_permissions(manage_channels = True)
async def createevent(ctx, arg : str):
    if arg == "bs":
        for guild in client.guilds:
            eventcategory = discord.utils.get(guild.categories, id = 853599647649234964)
            eventchat = await guild.create_text_channel(name = f'BS Режимы {ctx.author.name}', category = eventcategory)
            eventvoice = await guild.create_voice_channel(name = f'BS Режимы {ctx.author.name}', category = eventcategory)
            emb = discord.Embed(title = 'Новый ивент', colour = discord.Color.green())
            emb.add_field(name = 'BS режимы'.format(ctx), value = 'Ивент успешно создан!')
            await ctx.send(embed = emb)
    if arg == "codenames":
        for guild in client.guilds:
            eventcategory = discord.utils.get(guild.categories, id = 853599647649234964)
            eventchat = await guild.create_text_channel(name = f'Codenames {ctx.author.name}', category = eventcategory)
            eventvoice = await guild.create_voice_channel(name = f'Codenames {ctx.author.name}', category = eventcategory)
            emb = discord.Embed(title = 'Новый ивент', colour = discord.Color.green())
            emb.add_field(name = 'Коднеймс'.format(ctx), value = 'Ивент успешно создан!')
            await ctx.send(embed = emb)
    if arg == "alias":
        for guild in client.guilds:
            eventcategory = discord.utils.get(guild.categories, id = 853599647649234964)
            eventchat = await guild.create_text_channel(name = f'Alias {ctx.author.name}', category = eventcategory)
            eventvoice = await guild.create_voice_channel(name = f'Alias {ctx.author.name}', category = eventcategory)
            emb = discord.Embed(title = 'Новый ивент', colour = discord.Color.green())
            emb.add_field(name = 'Шляпа'.format(ctx), value = 'Ивент успешно создан!')
            await ctx.send(embed = emb)
    if arg == "other":
        for guild in client.guilds:
            eventcategory = discord.utils.get(guild.categories, id = 853599647649234964)
            eventchat = await guild.create_text_channel(name = f'Custom event {ctx.author.name}', category = eventcategory)
            eventvoice = await guild.create_voice_channel(name = f'Custom event {ctx.author.name}', category = eventcategory)
            emb = discord.Embed(title = 'Новый ивент', colour = discord.Color.green())
            emb.add_field(name = 'Кастомный ивент'.format(ctx), value = 'Ивент успешно создан!')
            await ctx.send(embed = emb)


@client.command()
@commands.has_permissions(manage_channels = True)
async def eventban(ctx, member:discord.Member, time:int, reason):
    eventban_role = discord.utils.get(ctx.message.guild.roles, name = 'Event Ban')

    await member.add_roles( eventban_role )

    emb = discord.Embed(description = f'{member.mention} отстранён от ивентов по причине: {reason}')
    await ctx.send(embed = emb)

    await asyncio.sleep(time * 60)
    emb = discord.Embed(description = f'У {member.mention} сняты ограничения!')
    await member.remove_roles(eventban_role)





@client.event
async def on_ready():
    print('Server runned. Bot connected to server')
    DiscordComponents(client)


@client.event
async def member_join( member ):
    channel = client.get_channel(834475151319498764)

    role = discord.utils.get( member.guild.roles, id = 835819972717576192 )

    await member.add_roles(role)
    await channel.send( embed = discord.Embed( description = f'Юзер ``{member.name}``, зашёл к нам на сервер',
                         color = 0x0c0c0c ) )


@client.event
async def on_message( message ):
    await client.process_commands( message )

    msg = message.content.lower()

    if msg in bad_words:
        await message.delete()
        await message.channel.send(f'{member.mention}, не матюкайся, а то мут)))')

        return


@client.command( pass_context = True )

async def say(ctx, arg):
    await ctx.channel.purge( limit = 1)
    author = ctx.message.author

    emb = discord.Embed( title = 'Повторялка', colour = discord.Color.green() )

    emb.set_author( name = client.user.name, icon_url = client.user.avatar_url )
    emb.set_footer( text = ctx.author.name, icon_url = ctx.author.avatar_url )

    emb.add_field( name = 'Повторяю:'.format(author), value = f'{ author.mention }' + arg, inline = False )

    await ctx.send( embed = emb )


@client.event

async def on_message( message ):
    await client.process_commands( message )
    msg = message.content.lower()

    if msg in hello_words:
        await message.channel.send('Привет!')

    if msg in answer_words:
        await message.channel.send('Я BriBot, меня создал юзер Brigis. Я пока не умею многого, но это сообщение ты не увидишь, ведь до релиза я многому обучусь)')


@client.command( pass_context = True )

async def clear(ctx, amount = 1000):
    await ctx.channel.purge( limit = amount )

    emb = discord.Embed(title = 'Очистка чата', color = discord.Color.green())

    emb.add_field(name = 'Было'.format(amount), value = f'Очищено {amount} сообщений!')

    await ctx.send(embed = emb)



@client.command( pass_context = True )
@commands.has_permissions(administrator = True)

async def kick(ctx, member: discord.Member, *, reason = None):
    await ctx.channel.purge( limit = 1 )

    await member.kick( reason = reason )

    emb = discord.Embed( title = 'Кик', colour = discord.Color.red() )

    emb.set_author( name = client.user.name, icon_url = client.user.avatar_url )
    emb.set_footer( text = ctx.author.name, icon_url = ctx.author.avatar_url )

    emb.add_field( name = 'Пользователь'.format(member), value = f'{ member.mention } был кикнут ', inline = False)
    emb.add_field( name = 'Причина:'.format(member), value = f'{reason}', inline = False)

    await ctx.send( embed = emb )


@client.command( pass_context = True )
@commands.has_permissions(administrator = True)

async def ban( ctx, member: discord.Member, *, reason = None ):
    await ctx.channel.purge( limit = 1 )

    await member.ban( reason = reason )

    emb = discord.Embed( title = 'Бан', colour = discord.Color.red() )

    emb.set_author( name = client.user.name, icon_url = client.user.avatar_url )
    emb.set_footer( text = ctx.author.name, icon_url = ctx.author.avatar_url )

    emb.add_field( name = 'Пользователь'.format(member), value = f'{ member.mention } был забанен по причине: {reason}', inline = False)

    await ctx.send( embed = emb )



@client.command( pass_context = True )
@commands.has_permissions( administrator = True )

async def unban( ctx, *, member ):
    await ctx.channel.purge( limit = 1 )

    banned_users = await ctx.guild.bans()

    for ban_entry in banned_users:
        user = ban_entry.user


        await ctx.guild.unban( user )

        emb = discord.Embed( title = 'Разбан', colour = discord.Color.green() )

        emb.set_author( name = client.user.name, icon_url = client.user.avatar_url )
        emb.set_footer( text = ctx.author.name, icon_url = ctx.author.avatar_url )

        emb.add_field( name = 'Пользователь'.format(user), value = f'{ user } был разбанен', inline = False)

        await ctx.send( embed = emb )


        return


@client.command()
async def help(ctx):

    emb = discord.Embed( title = 'Команды бота', colour = discord.Color.green() )

    emb.add_field(name = '====Модерация===='.format(ctx), value = 'Команды для модераторов', inline = False)
    emb.add_field(name = '{}kick'.format('>'), value = 'Кикает пользователя с сервера', inline = False)
    emb.add_field(name = '{}ban'.format('>'), value = 'Банит пользователя на сервере', inline = False)
    emb.add_field(name = '{}unban'.format('>'), value = 'Разбанивает пользователя на сервере',inline = False)
    emb.add_field(name = '{}mute'.format('>'), value = 'Ограничивает доступ к текстовым и голосовым каналам', inline = False)
    emb.add_field(name = '{}clear'.format('>'), value = 'Очищает чат', inline = False)
    emb.add_field( name = '====Музыка===='.format(ctx), value = 'Команды для голосовых каналов', inline = False )
    emb.add_field(name = '{}join'.format('>'), value = 'Бот присоединяется к голосовому каналу(нужно для команды play)', inline = False)
    emb.add_field(name = '{}leave'.format('>'), value = 'Бот выходит из голосового канала', inline = False)
    emb.add_field(name = '{}play'.format('>'), value = 'Команда для проигрывания музыки(после команды необоходимо указать ссылку на ютуб ролик с нужной композицией). Ожидать загрузки приходится мин. 1 минуту', inline = False)
    emb.add_field(name = '{}pause'.format('>'), value = 'Бот ставит песню на паузу', inline = False)
    emb.add_field(name = '{}resume'.format('>'), value = 'Бот убирает композицию с паузы', inline = False)
    emb.add_field( name = '====Экономика===='.format(ctx), value = 'Команды для экономики на сервере', inline = False )
    emb.add_field(name = '{}daily'.format('>'), value = 'Ежедневная награда', inline = False)
    emb.add_field(name = '{}balance'.format('>'), value = 'Баланс пользователя', inline = False)
    emb.add_field(name = '{}shop'.format('>'), value = 'Магазин ролей', inline = False)
    emb.add_field(name = '{}buy'.format('>'), value = 'Купить роль', inline = False)
    emb.add_field(name = '{}give'.format('>'), value = 'Передать деньги пользователю', inline = False)
    emb.add_field( name = '====Прочее===='.format(ctx), value = 'Прочие команды', inline = False )
    emb.add_field(name = '{}say'.format('>'), value = 'Повторяет написанное сообщение', inline = False)
    emb.add_field(name = '{}ucard'.format('>'), value = 'Собственная карточка пользователя', inline = False)


    await ctx.send(embed = emb)


@client.command()
@commands.has_permissions( view_audit_log = True )
async def mute( ctx, member:discord.Member,time:int, reason):
    await ctx.channel.purge( limit = 1 )

    mute_role = discord.utils.get(ctx.message.guild.roles, name = 'замучен')

    await member.add_roles( mute_role )

    emb = discord.Embed( title = 'Мут', colour = discord.Color.red() )

    emb.set_author( name = client.user.name, icon_url = client.user.avatar_url )

    emb.add_field( name = 'Пользователь'.format(member), value = f'{ member.mention } был замучен по причине: {reason}', inline = False)
    emb.add_field( name = 'Срок мута:', value = time, inline = False)
    emb.add_field( name = 'Модератор:', value = ctx.message.author.mention, inline = False )

    await ctx.send( embed = emb )
    await asyncio.sleep(time * 60)
    await member.remove_roles(mute_role)

    emb = discord.Embed( title = 'Размут', colour = discord.Color.green() )

    emb.add_field( name = 'У пользователя'.format(member), value = f'{ member.mention } истёк срок мута', inline = False)

    await ctx.send( embed = emb )


@client.command()
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f'Бот присоединился к {channel}')


@client.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()
        await ctx.send(f'Бот отключился от {channel}')


@client.command()
async def play(ctx, url : str):
    song_there = os.path.isfile('song.mp3')

    try:
        if song_there:
            os.remove('song.mp3')
            print('[log] Старый файл удалён ')
    except PermissionError:
        print('[log] Не удалось удалить файл')

    await ctx.send('Дождитесь конца загрузки...')

    voice = get(client.voice_clients, guild = ctx.guild)

    ydl_opts = {
        'format' : 'bestaudio/best',
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192'
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('[log] Загрузка музыки...')
        ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            print(f'[log] Переименовываю файл: {file}')
            os.rename(file, 'song.mp3')

    voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: print(f'[log] {name}, проигрывание окончено'))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.lolume = 0.07

    song_name = name.rsplit('-', 2)

    emb = discord.Embed( title = 'Музяка', colour = discord.Color.green() )

    emb.add_field( name = 'Сейчас играет:'.format(song_name), value = f'{ song_name }', inline = False)

    await ctx.send( embed = emb )



@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice.is_playing:
        voice.pause()
        await ctx.send('Пауза')
    else:
        await ctx.send('Сейчас не играет музыка!')


@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice.is_paused:
        voice.resume()
        await ctx.send('Воспроизведение снято с паузы')
    else:
        await ctx.send('Музыка не на паузе!')


@client.command()
async def ucard(ctx):
    await ctx.channel.purge( limit = 1 )
    img = Image.new('RGBA', (400, 200), '#B0E0E6')
    url = str(ctx.author.avatar_url)[:-10]


    response = requests.get(url, stream = True)
    response = Image.open(io.BytesIO(response.content))
    response = response.convert('RGBA')
    response = response.resize((100, 100), Image.ANTIALIAS)

    img.paste(response, (15, 15, 115, 115))

    idraw = ImageDraw.Draw(img)
    name = ctx.author.name
    tag = ctx.author.discriminator

    head_line = ImageFont.truetype('arial.ttf', size = 20)
    under_text = ImageFont.truetype('arial.ttf', size = 13)

    idraw.text((145, 15), f'{name}#{tag}', font = head_line)
    idraw.text((145, 50), f'{ctx.author.id}', font = under_text)


    img.save('user_card.png')

    await ctx.send(file = discord.File(fp = 'user_card.png'))



token = 'ODM0NDcxMTg2MjM0MjEyMzg0.YIBX2g.FWEg78kNPb_ZoRDhKh7D7jD2LXo'

client.run(token)
