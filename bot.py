#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import logging
import logging.handlers
import os
import OpenReports

import chatexchange.client
import chatexchange.events

hostID = 'stackoverflow.com'
roomID = '111347'
selfID = 7829893

commands = {'o':'normal', 'open':'normal', 'ir':'ignore_rest', 'ignore rest':'ignore_rest',
        'fa':'fetch_amount', 'fetch amount':'fetch_amount'}

helpmessage = \
        '    o, open:                    Open all reports not on ignore list\n' + \
        '    ir, ignore_rest:            Put all unhandled reports from you last querry on your ignore list\n' + \
        '    fa, fetch amount:           Display the number of unhandled reports\n' + \
        '    dil, delete ignorelist:     Delete your ignorelist\n' + \
        '    commands:                   Print this help'

def _parseMessage(msg):
    temp = msg.split()
    return ' '.join(v for v in temp if not v[0] == '@').lower()

def onMessage(message, client):
    if isinstance(message, chatexchange.events.MessagePosted) and message.content == '🚂':
        message.room.send_message('🚃')
        return

    amount = None
    try:
        if message.target_user_id != selfID:
            return
        userID = message.user.id
        command = _parseMessage(message.content)
        if command in ['a', 'alive']:
            message.message.reply('Yes.')
            return
        if command in ['dil', 'delete ignorelist']:
            os.remove(str(userID) + '.ignorelist')
            message.room.send_message('Ignorelist deleted.')
            return
        if command == 'commands':
            message.room.send_message(helpmessage)
            return
        if command.isdigit():
            mode = 'normal'
            amount = int(command)
        else:
            mode = commands[command]
    except:
        return
    
    message.message.reply(OpenReports.OpenReports(mode, userID=userID, amount=amount))


if 'ChatExchangeU' in os.environ:
    email = os.environ['ChatExchangeU']
else:
    email = input("Email: ")
if 'ChatExchangeP' in os.environ:
    password = os.environ['ChatExchangeP']
else:
    password = input("Password: ")

client = chatexchange.client.Client(hostID)
client.login(email, password)
print('Logged in')

room = client.get_room(roomID)
room.join()
print('Joined room')
room.send_message('Hi o/')

watcher = room.watch(onMessage)
watcher.thread.join()


client.logout()

