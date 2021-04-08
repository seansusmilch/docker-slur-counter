import logging as log
import logging
from os import path,mkdir
import sys
import json

import discord
from discord.abc import User
from tinydb import TinyDB
from bin.slurs import SlurCounter
from bin.users import Users
from bin.words import Words


def main():
    conf_path = '/config'
    logs_path = '/logs'
    data_path = '/data'

    # conf_path = './config'
    # logs_path = './logs'
    # data_path = './data'
    dir = path.split(path.abspath(__file__))[0]

    """
    Data folder structure setup
    """
    userfolder = f'{data_path}/users'
    if not path.exists(userfolder):
        print('Creating user folder in data')
        mkdir(userfolder)
    wordsfolder = f'{data_path}/words'
    if not path.exists(wordsfolder):
        print('Creating words folder in data')
        mkdir(wordsfolder)


    """
    Load Config
    """
    try:
        with open(f'{conf_path}/config.json') as f:
            data = json.load(f)
            discord_token = data['discord_token'].strip()
            if not discord_token or discord_token == "":
                print('Discord token is empty!!!')
                sys.exit(1)
            logging_level = data['logging_level']
            silence = data['silence']
            reactions = data['reactions']
            f.close()
    except:
        # create default secrets file
        with open(f'{conf_path}/config.json', 'w') as f:
            default = {
                'discord_token':"",
                'logging_level': 3,
                'silence': True,
                'reactions': True
            }
            json.dump(default,f,indent=2)
            f.close()
        print('Please edit the config.json file\nExiting...')
        input('hit enter to exit')
        sys.exit(1)

    """
    Logging
    """
    switcher = {
    4: log.DEBUG,
    3: log.INFO,
    2: log.WARNING,
    1: log.ERROR,
    0: log.CRITICAL
    }
    log.basicConfig(filename=f'{logs_path}/bot.log',
        level=switcher.get(logging_level, log.DEBUG),
        datefmt="%Y-%m-%d %H:%M:%S",
        format='%(asctime)s - %(levelname)s - %(message)s'
        )
    cons = log.StreamHandler()
    cons.setLevel(switcher.get(logging_level, log.DEBUG))
    fmt = log.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    cons.setFormatter(fmt)
    log.getLogger('').addHandler(cons)
    log.debug('Started!')

    db = TinyDB(f'{data_path}/db.json')
    user_tbl = db.table('users')
    # start bot
    users = Users(log, user_tbl)
    words = Words(data_path, log)
    bot = SlurCounter(discord_token, log, users, words, user_tbl,
        silence=silence, reactions=reactions)

if __name__ == '__main__':
    main()
