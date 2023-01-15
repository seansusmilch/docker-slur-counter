from texttable import Texttable
import discord
from discord.ext import commands
from tinydb import TinyDB

from bin.users import Users
from bin.words import Words
from bin.scores import Scores

class SlurCounter(commands.Bot):
    
    async def __init__(self, token, logging, usermod, wordmod, user_tbl,
            reactions = True,
            silence = True) -> None:
        
        intents = discord.Intents(messages=True, members=True, guilds=True)
        super().__init__(command_prefix='!', intents=intents)
        self.log = logging
        self.usr = usermod
        self.wrd = wordmod
        # logging.info(f'Using token {token}')
        self.log.info(f'Registering cogs')
        await self.add_cog(Scores(self, logging, usermod, wordmod, user_tbl))
        self.run(token)

    async def on_ready(self):
        self.log.info(f'{self.user.name} has connected to Discord!')

    async def on_command_error(self, ctx, err):
        if isinstance(err, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')