import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import confuse
from pathlib import Path
import sys
import logging


folder = Path(__file__).parent.absolute()
conf = confuse.Configuration('WhosOn', __name__)
possible_config = [
    f'{folder}/config.yml',
    f'{folder}/config.yaml',
    f'/config/config.yml',
    f'/config/config.yaml',
    f'/data/config.yml',
    f'/data/config.yaml'
]
conf_file = Path( possible_config.pop(0) )
while not conf_file.exists():
    if not possible_config:
        print('Config file not found!!!')
        sys.exit(1)
    conf_file = Path( possible_config.pop(0) )
print(f'Using config file at {conf_file}')
conf.set_file(conf_file)

def logging_setup():
    logging_level = conf['loglevel'].get(int)
    switcher = {
        4: logging.DEBUG,
        3: logging.INFO,
        2: logging.WARNING,
        1: logging.ERROR,
        0: logging.CRITICAL
    }
    logging.basicConfig(
        level=switcher.get(logging_level, logging.DEBUG),
        datefmt="%Y-%m-%d %H:%M:%S",
        format='%(asctime)s - %(levelname)s - %(message)s'
        )
    logging.getLogger('')
    logging.debug('Started script!')

if __name__ == '__main__':
    from web import app
    logging_setup()
    asyncio.run(serve(app, Config.from_mapping(conf['hypercorn'].get())))