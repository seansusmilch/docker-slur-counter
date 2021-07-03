$files = @(
    './requirements.txt'
    './bot.py'
    './Dockerfile'
    './prod.py'
    './web.py'
    './.dockerignore'
    './bin'
    './fonts'
)

# Clear cache before making tar
Get-ChildItem -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse

tar -czvf whos-on.tar.gz $files