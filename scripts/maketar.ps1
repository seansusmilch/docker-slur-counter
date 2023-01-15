# Set-Location '../'
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

mkdir builds
tar -czvf builds/slur-counter.tar.gz $files