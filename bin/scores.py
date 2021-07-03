from bin.words import Words
from bin.users import Users
from os import mkdir, path
import logging as log

import discord
import numpy as np
from discord.errors import InvalidArgument
from discord.ext import commands
from texttable import Texttable

# from bin.users import Users
# from bin.words import Words
from PIL import Image, ImageDraw, ImageFont
from tinydb import TinyDB, where


class Scores(commands.Cog):

    def __init__(self, bot, data_path:str,
            reactions = True,
            silence = True) -> None:
        log.info('Loading Scores cog...')
        db = TinyDB(f'{data_path}/db.json')
        user_tbl = db.table('users')
        self.bot = bot
        self.usr = Users(user_tbl)
        self.wrd = Words(data_path)
        self.user_tbl = user_tbl
        self.reactions = reactions
        self.silence = silence

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author == self.bot.user or message.author.bot:
            return
        # await self.bot.process_commands(message)
        log.info('Someone said...')
        nouns = self.wrd.getNouns()
        word_lists = self.wrd.getWordLists()
        log.debug(f'loaded words from {str(nouns)}')

        for word_list in word_lists:
            n = nouns[word_lists.index(word_list)]
            for word in word_list:
                if word in message.content.lower():
                    if not self.silence:
                        await message.channel.send(f"<@{message.author.id}> is a certified {n}" )
                    if self.reactions:
                        await message.add_reaction("😱")
                    self.usr.add_entry(word,message)

    @commands.command(name='scores', help='Usage: scores <category> <format>\n\nShows the scoreboard for a certain category of word. Use the "all" category to show scores for all categories. Use !scores with no arguments to show a list of available categories.\n\nAvaliable formats: text,img')
    async def scoreboard(self, ctx,
            cat='none',
            fmt='img'):
        
        log.info(f'Processing args: cat="{cat}" fmt="{fmt}"')

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
                        log.error(f'invalid output from get_score {user},{guild},{noun}')
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
                    continue
                scores[u.name] = self.get_score(u, guild, noun=cat)

            # scores from highest to lowest
            scores_ordered = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

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
            log.info(f'Successfully created scoreboard. "{board[:10]}"')
        else:
            log.warning(f'Unable to create board')
        # send in the desired format (text or image)
        if fmt == 'text':
            board = f'```text\n{board}\n```'
            await ctx.send(board)
            return
        elif fmt == 'img':
            log.info(f'Creating image for board.')
            ipath = self.text_to_img(board)
            log.info(f'Opening image from {ipath}')
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
            log.error('Invalid inputs to get_score')
            raise InvalidArgument()
        if user.bot:
            log.warning(f'{user.name} is a bot! Not keeping score')
            raise InvalidArgument()
        if word:
            log.info('Single word score not implemented yet.')
            return -1
        
        log.info(f'Getting score for {user.name} - {noun}')
        if noun:
            word_list = self.wrd.getWordList(noun)
            count = 0
            all_evidence = self.user_tbl.get(where('uid')==user.id)
            # print(all_evidence)
            if not all_evidence:
                log.info('No evidence found :(')
                return count
            for word in word_list:
                if word not in all_evidence.keys():
                    continue
                evidence = list(all_evidence[word])
                count += len(evidence)

            log.info(count)
            return count

    def text_to_img(self, board : str) -> str:
        """
        This function will return the absolute file path to the generated image
        """
        font_path = 'fonts/SourceCodePro-SemiBold.ttf'
        font_size = 16
        txt_color = 'white'
        save_path = 'img/latest.png'

        # check if save_path exists
        if not path.exists('img'):
            mkdir('img')
            log.info('Image folder created.')

        log.info('Creating image...')
        try:
            image = Image.new('RGB', (1000,1000),)
            font = ImageFont.truetype(font_path, font_size)
            draw = ImageDraw.Draw(image)
            draw.text((30,30), board, fill=txt_color, font=font)
        except Exception as ex:
            log.error(f'Whoopsies {ex}')
            raise

        # crop
        log.info('Cropping image...')
        image.load()

        image_data = np.asarray(image)
        image_data_bw = image_data.max(axis=2)
        non_empty_columns = np.where(image_data_bw.max(axis=0)>0)[0]
        non_empty_rows = np.where(image_data_bw.max(axis=1)>0)[0]
        cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))

        image_data_new = image_data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 , :]

        new_image = Image.fromarray(image_data_new)

        log.info('Saving image')
        new_image.save(save_path)

        return path.abspath(save_path)        
