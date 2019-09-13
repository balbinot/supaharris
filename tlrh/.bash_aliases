alias myip="dig +short myip.opendns.com @resolver1.opendns.com"
alias ips="ifconfig -a | perl -nle'/(\d+\.\d+\.\d+\.\d+)/ && print $1'"
alias ping="ping -c 5"
alias ls="ls -GlhF"
alias rm='rm -vi'
alias cp='cp -vi'
alias mv='mv -vi'
alias grep="grep -n --color="auto""
alias gcc='gcc -ansi -std=c99 -Wall -pedantic'
alias g++='\gcc -lstdc++ -Wall'
alias javac='javac -Xlint'
alias make='make -j8'
alias refresh="touch uwsgi/*.ini"
alias manage="python manage.py"
alias check="python manage.py check"
alias shell="python manage.py shell"
alias shell_plus="python manage.py shell_plus"
alias dbshell="python manage.py dbshell"
alias makemigrations="python manage.py makemigrations"
alias migrate="python manage.py migrate"
alias collectstatic="python manage.py collectstatic --noinput -i node_modules -i gulpfile.js -i package.json -i package-lock.json"
