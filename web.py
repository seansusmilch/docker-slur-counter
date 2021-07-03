from quart import Quart, request
from bot import EpicDiscordBot
import asyncio
from prod import conf

DISCORD_TOKEN = conf['discord']['bot_token'].get()
CHANNEL_ID = conf['discord']['channel_id'].get()
DATA_PATH = conf['discord']['slur_data'].get(str)

API_KEY = conf['shortcut']['key'].get()

app = Quart(__name__)

@app.before_serving
async def before_serving():
    loop = asyncio.get_event_loop()
    app.discord_client = EpicDiscordBot(DATA_PATH)
    loop.create_task(app.discord_client.start(DISCORD_TOKEN))

@app.route('/whoson', methods=['GET'])
async def whoson():
    if not request.headers.get('x-key') == API_KEY:
        return '<h1>Bad request</h1>', 400
    
    members = await app.discord_client.get_connected_voice(CHANNEL_ID)
    # members += members
    if not members:
        return 'No one is on right now'
    
    if len(members) == 1:
        return f'{members[0]} is on right now'

    if len(members) == 2:
        return ', '.join(members[0:len(members)-1]) + f' and {members[-1]} are on right now.'

    return ', '.join(members[0:len(members)-1]) + f', and {members[-1]} are on right now.'

if __name__ == '__main__':
    
    QUART_HOST = conf['quart']['host'].get()
    QUART_PORT = conf['quart']['port'].get()
    app.run(host=QUART_HOST, port=QUART_PORT)