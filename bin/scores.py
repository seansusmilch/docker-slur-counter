import discord
from discord.errors import InvalidArgument
from discord.ext import commands
from texttable import Texttable

from bin.users import Users
from bin.words import Words


class Scores(commands.Cog):

    def __init__(self, bot, logging, usermod, wordmod,
            reactions = True,
            silence = True) -> None:

        self.bot = bot
        self.usr = usermod
        self.wrd = wordmod
        self.logging = logging
        self.reactions = reactions
        self.silence = silence

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return
        # await self.bot.process_commands(message)
        
        nouns = self.wrd.getNouns()
        word_lists = self.wrd.getWordLists()
        self.logging.debug('loaded words from %s' % str(nouns))

        for word_list in word_lists:
            n = nouns[word_lists.index(word_list)]
            for word in word_list:
                if word in message.content.lower():
                    if not self.silence:
                        await message.channel.send("<@%s> is a certified %s" % (message.author.id, n))
                    if self.reactions:
                        await message.add_reaction("😱")
                    self.usr.add_entry(word,message)

    @commands.command(name='scores', help='Usage: scores <category>\nShows the scoreboard for a certain category of word. Use the "all" category to show scores for all categories.')
    async def scoreboard(self, ctx,
            arg='categories'):

        args = arg.split(' ')
        print('ARGS=', args)

        if len(args) > 1:
            await ctx.send('Too many arguments!')
            return

        nouns = self.wrd.getNouns()

        if args[0] == 'categories':
            msg = 'Category required\n```text\nAvailable Categories:\n\tall\n'
            for n in nouns:
                msg = msg + f'\t{n}\n'
            msg = msg + '\n```'
            await ctx.send(msg)
            return
        
        if args[0] != 'all' and args[0] not in nouns:
            await ctx.send('That category is not available. Use the scores command without any arguments to see available categories.')
            return
        guild = ctx.message.guild
        userls = guild.members

        scores = dict()

        if args[0] != 'all':
            word_list = self.wrd.getWordList(args[0])

            for u in userls:
                if u.bot:
                    userls.remove(u)
                    continue

                count = 0

                data = self.usr.readUsrJson(u.id)
                if isinstance(data, str):
                    self.logging.warning(f'{u.name} - {data}')
                    scores[u.name] = count
                    continue

                data = data['servers'][str(guild.id)]   # trim it down
                for word in data.keys():
                    if word in word_list:
                        evidence = data[word]['evidence']
                        count = count + len(evidence)
                
                self.logging.info(f'Found evidence that {u.name} is a {args[0]}, count={count}')
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

        # Response for 'all' category below

        table = Texttable()
        table.set_deco(Texttable.HEADER)

        align = ['r', 'l']
        vals = [['Scores', 'Name']]
        gscores = {noun: 0 for noun in nouns}

        for user in userls:
            if user.bot:
                continue
            scores[user.name] = dict()
            total = 0
            for noun in nouns:
                new = self.get_score(user,guild,noun=noun)
                if new < 0:
                    print(f'invalid output from get_score {user},{guild},{noun}')
                gscores[noun] += new
                total += new
                scores[user.name][noun] = new

            scores[user.name]['total'] = total

        gscores = dict(sorted(gscores.items(), key=lambda x: x[1], reverse=True))
        scores = dict(sorted(scores.items(), key=lambda x: x[1]['total'], reverse=True))

        for k in gscores.keys():
            vals[0].append(f'{k[:5]}\n{gscores[k]}')
            align.append('c')

        for user in scores.keys():
            row = [str(scores[user]['total']), user]
            for cat in gscores.keys():
                row.append(str(scores[user][cat]))
            vals.append(row)
        table.set_cols_align(align)
        table.add_rows(vals)
        await ctx.send(f'```{table.draw()}```')




    

    def get_score(self, user, guild,
            noun = None,
            word = None) -> int:

        if noun == None and word == None:
            self.logging.error('Invalid inputs to get_score')
            raise InvalidArgument()
        if user.bot:
            self.logging.warning(f'{user.name} is a bot! Not keeping score')
            raise InvalidArgument()

        count = 0
        data = self.usr.readUsrJson(user.id)
        if isinstance(data, str):
            self.logging.warning(f'JSON was read as string!{user.name} - {data}')
            return count        
        data = data['servers'][str(guild.id)]   # trim it down

        if noun:
            word_list = self.wrd.getWordList(noun)
            for word in data.keys():
                if word in word_list:
                    evidence = data[word]['evidence']
                    count = count + len(evidence)
            
            if count > 0:
                self.logging.info(f'Found evidence that {user.name} is a {noun}, count={count}')
            else:
                self.logging.info(f'Looks like {user.name} is clean...')

            return count
        if word:
            self.logging.info('Single word score not implemented yet.')
            return -1
