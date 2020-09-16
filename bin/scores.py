from os import mkdir, path
import sys

import discord
import numpy as np
from discord.errors import InvalidArgument
from discord.ext import commands
from texttable import Texttable

# from bin.users import Users
# from bin.words import Words
from PIL import Image, ImageDraw, ImageFont


class Scores(commands.Cog):

    def __init__(self, bot, logging, usermod, wordmod,
            reactions = True,
            silence = True) -> None:

        self.bot = bot
        self.usr = usermod
        self.wrd = wordmod
        self.log = logging
        self.reactions = reactions
        self.silence = silence

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return
        # await self.bot.process_commands(message)
        
        nouns = self.wrd.getNouns()
        word_lists = self.wrd.getWordLists()
        self.log.debug('loaded words from %s' % str(nouns))

        for word_list in word_lists:
            n = nouns[word_lists.index(word_list)]
            for word in word_list:
                if word in message.content.lower():
                    if not self.silence:
                        await message.channel.send("<@%s> is a certified %s" % (message.author.id, n))
                    if self.reactions:
                        await message.add_reaction("😱")
                    self.usr.add_entry(word,message)

    @commands.command(name='scores', help='Usage: scores <category> <format>\n\nShows the scoreboard for a certain category of word. Use the "all" category to show scores for all categories. Use !scores with no arguments to show a list of available categories.\n\nAvaliable formats: text,img')
    async def scoreboard(self, ctx,
            cat='none',
            fmt='img'):
        
        self.log.info(f'Processing args: cat="{cat}" fmt="{fmt}"')

        guild = ctx.message.guild
        userls = guild.members
        scores = dict()
        nouns = self.wrd.getNouns()

        if cat == 'none':
            msg = 'Category required\n```text\nAvailable Categories:\n\tall\n'
            for n in nouns:
                msg = msg + f'\t{n}\n'
            msg = msg + '\n```'
            await ctx.send(msg)
            return
        
        elif cat == 'all':

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
                vals[0].append(f'{k[:10]}\n{gscores[k]}')
                align.append('c')

            for user in scores.keys():
                row = [str(scores[user]['total']), user]
                for cat in gscores.keys():
                    row.append(str(scores[user][cat]))
                vals.append(row)
            table.set_cols_align(align)
            table.add_rows(vals)
            board = table.draw()

        elif cat in nouns:
            word_list = self.wrd.getWordList(cat)

            for u in userls:
                if u.bot:
                    userls.remove(u)
                    continue

                count = 0

                data = self.usr.readUsrJson(u.id)
                if isinstance(data, str):
                    self.log.warning(f'{u.name} - {data}')
                    scores[u.name] = count
                    continue

                data = data['servers'][str(guild.id)]   # trim it down
                for word in data.keys():
                    if word in word_list:
                        evidence = data[word]['evidence']
                        count = count + len(evidence)
                
                self.log.info(f'Found evidence that {u.name} is a {cat[0]}, count={count}')
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

            board = 'Word List:'
            board += "".join(f'\n - {x}' for x in word_list)
            board += '\n'
            board += '\n' + table.draw()
            
        else:
            await ctx.send('That category is not available. Use the scores command without any arguments to see available categories.')
            return

        if board:
            self.log.info(f'Successfully created scoreboard. "{board[:10]}"')
        else:
            self.log.warning(f'Unable to create board')
        # send in the desired format (text or image)
        if fmt == 'text':
            board = f'```text\n{board}\n```'
            await ctx.send(board)
            return
        elif fmt == 'img':
            self.log.info(f'Creating image for board.')
            ipath = self.text_to_img(board)
            self.log.info(f'Opening image from {ipath}')
            with open(ipath, 'rb') as f:
                img = discord.File(f)
                f.close()
            await ctx.send(file=img)
            return
        else:
            await ctx.send(f'Unknown format argument "{fmt}"-')




    

    def get_score(self, user, guild,
            noun = None,
            word = None) -> int:

        if noun == None and word == None:
            self.log.error('Invalid inputs to get_score')
            raise InvalidArgument()
        if user.bot:
            self.log.warning(f'{user.name} is a bot! Not keeping score')
            raise InvalidArgument()

        count = 0
        data = self.usr.readUsrJson(user.id)
        if isinstance(data, str):
            self.log.warning(f'JSON was read as string!{user.name} - {data}')
            return count        
        data = data['servers'][str(guild.id)]   # trim it down

        if noun:
            word_list = self.wrd.getWordList(noun)
            for word in data.keys():
                if word in word_list:
                    evidence = data[word]['evidence']
                    count = count + len(evidence)
            
            if count > 0:
                self.log.info(f'Found evidence that {user.name} is a {noun}, count={count}')
            else:
                self.log.info(f'Looks like {user.name} is clean...')

            return count
        if word:
            self.log.info('Single word score not implemented yet.')
            return -1


    def text_to_img(self, board : str) -> str:
        """
        This function will return the absolute file path to the generated image
        """
        font_path = 'fonts/SourceCodePro-SemiBold.ttf'
        font_size = 16
        txt_color = 'white'

        from glob import glob
        print(glob('./*'))
        save_path = 'img/latest.png'

        # check if save_path exists
        if not path.exists('img'):
            mkdir('img')
            self.log.info('Image folder created.')

        self.log.info('Creating image...')
        try:
            image = Image.new('RGB', (1000,1000),)
            font = ImageFont.truetype(font_path, font_size)
            draw = ImageDraw.Draw(image)
            draw.text((30,30), board, fill=txt_color, font=font)
        except Exception as e:
            print(sys.exc_info())
            print(e)
            raise

        # crop
        self.log.info('Cropping image...')
        image.load()

        image_data = np.asarray(image)
        image_data_bw = image_data.max(axis=2)
        non_empty_columns = np.where(image_data_bw.max(axis=0)>0)[0]
        non_empty_rows = np.where(image_data_bw.max(axis=1)>0)[0]
        cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))

        image_data_new = image_data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 , :]

        new_image = Image.fromarray(image_data_new)

        self.log.info('Saving image')
        new_image.save(save_path)

        return path.abspath(save_path)        
