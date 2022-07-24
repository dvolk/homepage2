## Development reloading

cd denispage
watchmedo shell-command --pattern '*.j2' --command 'cd ..;python3 main.py denispage'

## Deployment

rsync -aXxv -e "ssh -p 44444" denispage-out/ ubuntu@eclipse.oxfordfun.com:/var/www/html/denis
