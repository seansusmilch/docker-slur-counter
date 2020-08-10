import sys
from os import path,mkdir
from glob import glob
import ntpath
from texttable import Texttable

dir = path.split(path.abspath(__file__))
dir = dir[0]

conf_path = '/config'
logs_path = '/logs'
data_path = '/data'

# conf_path = './config'
# logs_path = './logs'
# data_path = './data'

# data folder structure setup
userfolder = f'{data_path}/users'
if not path.exists(userfolder):
    print('Creating user folder in data')
    mkdir(userfolder)
wordsfolder = f'{data_path}/words'
if not path.exists(wordsfolder):
    print('Creating words folder in data')
    mkdir(wordsfolder)

import json
try:
    with open(f'{conf_path}/config.json') as f:
        data = json.load(f)
        discord_token = data['discord_token'].strip()
        if not discord_token or discord_token == "":
            print('Discord token is empty!!!')
            sys.exit(1)
        logging_level = data['logging_level']
        f.close()
except:
    # create default secrets file
    with open(f'{conf_path}/config.json', 'w') as f:
        default = {
            'discord_token':"",
            'logging_level': 4
        }
        json.dump(default,f,indent=2)
        f.close()
    print('Please edit the config.py file\nExiting...')
    input('hit enter to exit')
    sys.exit(1)

# try:
#     from config import discord_token,logging_level
# except ImportError as e:
#     # create default secrets file
#     with open(dir+'/config.py', 'x') as f:
#         f.write("discord_token = ''\nlogging_level = ")
#         f.close()
#     print('Please edit the config.py file\nExiting...')
#     input()
#     sys.exit(1)

#logging
import logging
switcher = {
    4: logging.DEBUG,
    3: logging.INFO,
    2: logging.WARNING,
    1: logging.ERROR,
    0: logging.CRITICAL
}
logging.basicConfig(filename=f'{logs_path}/bot.log',
    level=switcher.get(logging_level, logging.DEBUG),
    datefmt="%Y-%m-%d %H:%M:%S",
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
cons = logging.StreamHandler()
cons.setLevel(switcher.get(logging_level, logging.DEBUG))
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
cons.setFormatter(fmt)
logging.getLogger('').addHandler(cons)
logging.debug('Started!')

import datetime

def writeToJson(raw_data, filepath):
    with open(filepath, 'w') as f:
        json.dump(raw_data, f)
        f.close()

def readUsrJson(user_id :str):
    json_file = f'{data_path}/users/{user_id}.json'
    logging.info(f'Attempting to read json from {json_file}')
    try:
        with open(json_file) as f:
            data = json.load(f)
            f.close()
        logging.warning(f'JSON for {user_id} loaded!')
        return data
    except json.decoder.JSONDecodeError as e:
        logging.error('Couldnt retrieve json file for %s!' % user_id)
        return 1
    except FileNotFoundError as e:
        logging.error(f'File not found. {json_file}')
        return 2



def add_entry(word :str, message):
    user_id = message.author.id
    server_id = str(message.guild.id)
    message_link = 'https://discordapp.com/channels/%s/%s/%s' % (server_id, message.channel.id, message.id)
    # json_file = '%s/data/users/%s.json' % (dir, user_id)
    json_file = f'{data_path}/users/{user_id}.json'

    new_evidence = {
        "timeSent": str(message.created_at),
        "message": message.content,
        "link": message_link
    }

    new_word = {
        word:{
            "evidence":[new_evidence]
        }
    }

    new_server = {
        server_id:new_word
    }

    try:
        with open(json_file) as f:
            data = json.load(f)
            f.close()
        logging.info('JSON for %s loaded!' % message.author)
    except json.decoder.JSONDecodeError as e:
        logging.critical(f'Error loading JSON! {json_file}')
    except FileNotFoundError as e:
        first = {
            "servers": new_server
        }
        writeToJson(first, json_file)
        return

    # see if server exists, add new server if not

    try:
        data['servers'][server_id]
    except KeyError as e:
        data['servers'].update(new_server)
        writeToJson(data, json_file)
        return

    # if data['servers'][server_id] == None:
    #     data['servers'][server_id] = new_server
    #     writeToJson(data)
    #     return
    
    # see if word exists, add new word if not

    try:
        data['servers'][server_id][word]
    except KeyError as e:
        data['servers'][server_id].update(new_word)
        writeToJson(data, json_file)
        return
        
    # add evidence

    data['servers'][server_id][word]['evidence'].append(new_evidence)
    writeToJson(data, json_file)
    return

        

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)
    # get words from words files
    word_files = glob(f'{data_path}/words/*.txt')
    # word_files = glob('%s/data/words/*.txt' % dir)
    nouns = [ntpath.basename(f).replace('.txt','') for f in word_files]
    word_lists = []
    for word_file in word_files:
        with open(word_file) as f:
            ls = f.readlines()
            lsstrip = [x.strip() for x in ls]
            word_lists.append(lsstrip)
            f.close()
    logging.debug('loaded words from %s' % str(nouns))

    for word_list in word_lists:
        n = nouns[word_lists.index(word_list)]
        for word in word_list:
            if word in message.content:
                await message.channel.send("<@%s> is a certified %s" % (message.author.id, n))
                add_entry(word,message)

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@bot.command(name='scores', help='Usage: scores <category>\nShows the scoreboard for a certain category of word. Use the "all" category to show scores for all categories.')
async def scoreboard(ctx, arg='categories'):
    print('ARGS: "',arg,'"')
    args = arg.split(' ')
    print(args)

    if len(args) > 1:
        await ctx.send('Too many arguments!')
        return

    # word_files = glob('%s/data/words/*.txt' % dir)
    word_files = glob(f'{data_path}/words/*.txt')
    nouns = [ntpath.basename(f).replace('.txt','') for f in word_files]
    word_lists = []
    for word_file in word_files:
        with open(word_file) as f:
            ls = f.readlines()
            lsstrip = [x.strip() for x in ls]
            word_lists.append(lsstrip)
            f.close()
    logging.warning('loaded words from %s' % str(nouns))

    if args[0] == 'categories':
        msg = 'Category required\n```text\nAvailable Categories:\n'
        # msg = msg + ('\t%s\n' % (x for x in nouns))
        for n in nouns:
            msg = msg + f'\t{n}\n'
        msg = msg + '\n```'
        await ctx.send(msg)
        return
    
    if args[0] not in nouns:
        await ctx.send('That category is not available. Use the scores command without any arguments to see available categories.')
        return
    guild = ctx.message.guild
    users = guild.members



    scores = dict()

    if args[0] != 'all':
        word_list = word_lists[nouns.index(args[0])]

        for usr in users:
            if usr.bot:
                users.remove(usr)
                continue

            count = 0
            logging.warning(f'Looking for evidence that {usr.name} is a {args[0]}')

            data = readUsrJson(usr.id)
            if data == 1 or data == 2:
                scores[usr.name] = count
                continue

            data = data['servers'][str(guild.id)]
            for word in data.keys():
                if word in word_list:
                    evidence = data[word]['evidence']
                    count = count + len(evidence)
            
            scores[usr.name] = count

        # scores from highest to lowest
        scores_ordered = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
        print(bot.user.name)
        del scores_ordered[bot.user.name]
        print('scores=',scores_ordered)


        # create the scoreboard
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(['r','l'])
        vals = [['Score','Name']]
        for n in scores_ordered:
            row = [str(scores_ordered[n]),n]
            vals.append(row)
        table.add_rows(vals)



        board = '```text\nWord List:'
        board = board + "".join(f'\n\t{x}' for x in word_list)
        board = board + '\n'
        # board = board + "".join(f'\n\t{scores_ordered[n]}\t{n}' for n in scores_ordered)
        board = board + '\n' + table.draw()

        board = board + '\n```'
        await ctx.send(board)

print('Using token="'+discord_token+'" dont worry this will not be in bot.log')
bot.run(discord_token)