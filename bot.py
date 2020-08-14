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


"""
Load Config
"""
import json
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
            'logging_level': 4,
            'silence': False,
            'reactions': True
        }
        json.dump(default,f,indent=2)
        f.close()
    print('Please edit the config.py file\nExiting...')
    input('hit enter to exit')
    sys.exit(1)

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
     
import discord
from discord.ext import commands

from bin.users import Users
from bin.words import Words

usr = Users(data_path, logging)
wrd = Words(data_path, logging)

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)
    
    nouns = wrd.getNouns()
    word_lists = wrd.getWordLists()
    logging.debug('loaded words from %s' % str(nouns))

    for word_list in word_lists:
        n = nouns[word_lists.index(word_list)]
        for word in word_list:
            if word in message.content.lower():
                if not silence:
                    await message.channel.send("<@%s> is a certified %s" % (message.author.id, n))
                if reactions:
                    await message.add_reaction("😱")
                usr.add_entry(word,message)

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@bot.command(name='scores', help='Usage: scores <category>\nShows the scoreboard for a certain category of word. Use the "all" category to show scores for all categories.')
async def scoreboard(ctx, arg='categories'):
    args = arg.split(' ')
    print('ARGS=', args)

    if len(args) > 1:
        await ctx.send('Too many arguments!')
        return

    nouns = wrd.getNouns()

    if args[0] == 'categories':
        msg = 'Category required\n```text\nAvailable Categories:\n'
        for n in nouns:
            msg = msg + f'\t{n}\n'
        msg = msg + '\n```'
        await ctx.send(msg)
        return
    
    if args[0] not in nouns:
        await ctx.send('That category is not available. Use the scores command without any arguments to see available categories.')
        return
    guild = ctx.message.guild
    userls = guild.members



    scores = dict()

    if args[0] != 'all':
        word_list = wrd.getWordList(args[0])

        for u in userls:
            if u.bot:
                userls.remove(u)
                continue

            count = 0

            data = usr.readUsrJson(u.id)
            if isinstance(data, str):
                logging.warning(f'{u.name} - {data}')
                scores[u.name] = count
                continue

            data = data['servers'][str(guild.id)]   # trim it down
            for word in data.keys():
                if word in word_list:
                    evidence = data[word]['evidence']
                    count = count + len(evidence)
            
            logging.info(f'Found evidence that {u.name} is a {args[0]}, count={count}')
            scores[u.name] = count

        # scores from highest to lowest
        scores_ordered = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
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
        board = board + '\n' + table.draw()

        board = board + '\n```'
        
        await ctx.send(board)

    table = Texttable()
    table.set_deco(Texttable.HEADER)


print('Using token="'+discord_token+'" dont worry this will not be in bot.log')
bot.run(discord_token)