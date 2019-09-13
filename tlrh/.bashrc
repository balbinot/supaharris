# Set command completion case insensitive. Only if running interactively.
[ ! -z "$PS1" ] && bind "set completion-ignore-case on"

# Set the prompt
# PS1="[\$(date +%H:%M:%S)][\u@\h]$\[\033[0m\] "

# Aliases
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# Functions
if [ -f ~/.bash_functions ]; then
    . ~/.bash_functions
fi

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=10000
HISTFILESIZE=20000

# Do not override when using '>', '>&' and '>>' redirection operators
set -o noclobber

# Get them lovely VI bindings bro. 
set -o vi

export EDITOR=vim
export IPYTHONDIR=/supaharris/.ipython
