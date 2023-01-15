import tarfile
from pathlib import Path

files = [
    'requirements.txt',
    'bot.py',
    'Dockerfile',
    'prod.py',
    'web.py',
    '.dockerignore',
    'bin/',
    'fonts/'
]

here = Path(__file__).parent.parent
builds = Path(f'{here}/build')

new_build = Path(f'{builds}/slurs-counter.tar')


tar = tarfile.open(new_build, 'w')
for file in files:
    print(f'Adding {file}')
    tar.add(file, recursive=True)
tar.close()