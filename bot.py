#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import logging
import logging.handlers
import os
import OpenReports
from subprocess import call

import chatexchange.client
import chatexchange.events

hostID = 'stackoverflow.com'
roomID = '111347'
selfID = 7829893

commands = {'o':'normal', 'open':'normal', 'ir':'ignore_rest', 'ignore rest':'ignore_rest',
        'fa':'fetch_amount', 'fetch amount':'fetch_amount'}

helpmessage = \
        '    o, open:                    Open all reports not on ignore list\n' + \
        '    `number` [b[back]]:         Open up to `number` reports, fetch from the back of the list if b or back is present\n' + \
        '    ir, ignore rest:            Put all unhandled reports from you last querry on your ignore list\n' + \
        '    fa, fetch amount:           Display the number of unhandled reports\n' + \
        '    dil, delete ignorelist:     Delete your ignorelist\n' + \
        '    reboot open:                Restart the open reports bot'

def _parseMessage(msg):
    temp = msg.split()
    return ' '.join(v for v in temp if not v[0] == '@').lower()

def onMessage(message, client):
    if isinstance(message, chatexchange.events.MessagePosted) and message.content in ['🚂', '🚆']:
        message.room.send_message('[🚃](https://github.com/SOBotics/Open-Reports)')
        return

    amount = None
    fromTheBack = False
    try:
        if message.target_user_id != selfID:
            return
        userID = message.user.id
        command = _parseMessage(message.content)
        words = command.split()
        if command == 'reboot open':
            os._exit(1)
        if command == 'update open':
            call(['git', 'pull'])
            os._exit(1)
        if command in ['a', 'alive']:
            message.room.send_message('[open] Yes.')
            return
        if command in ['dil', 'delete ignorelist']:
            os.remove(str(userID) + '.ignorelist')
            message.room.send_message('Ignorelist deleted.')
            return
        if command == 'commands open':
            message.room.send_message(helpmessage)
            return
        if words[0].isdigit():
            mode = 'normal'
            amount = int(words[0])
            if len(words) > 1:
                if len(words) > 2 or words[1] not in ['b', 'back']:
                    return
                fromTheBack = True
        else:
            mode = commands[command]
    except:
        return
    
    message.room.send_message(OpenReports.OpenReports(mode, userID=userID, amount=amount,
        back=fromTheBack))


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
room.send_message('[open] Hi o/')

watcher = room.watch(onMessage)
watcher.thread.join()


client.logout()

