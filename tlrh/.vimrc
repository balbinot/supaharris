let $VIM='~/.vim/'

" Change color scheme for better contrast on dark background.
set background=dark

set nocp

" VIM improvements.
set showcmd          " Show (partial) command in status line.
set showmatch        " Show matching brackets.
set ignorecase       " Do case insensitive matching
set smartcase        " Do smart case matching
set incsearch        " Incremental search
set autowrite        " Automatically save before commands like :next and :make
set hidden           " Hide buffers when they are abandoned
set mouse=a          " Enable mouse usage (all modes)

" TLRH improvements.
set autoindent
set smartindent
set shiftwidth=4
set expandtab
set list
set tabstop=4
set softtabstop=4
" set textwidth=80
set colorcolumn=80
set wrap
set history=500         " keep 500 lines of history
set ruler               " show the cursor position
set hlsearch            " highlight the last searched term
set wildmenu " vsp: <tab>
set statusline=\ %F%m%r%h\ %w\ \ CWD:\ %r%{CurDir()}%h\ \ \ Line:\ /%L:%c
set backspace=eol,start,indent
set tabpagemax=42

" Show and print linenumbers
set number
set printoptions=number:y

" Set up folding (for Python)
set nofoldenable  " disable folding by default? :-)
set foldmethod=manual
set foldnestmax=2

" Enable Syntax Highlighting
if has("syntax")
    syntax on
endif

if has("autocmd")
    " Jump cursor to last position when reopening a file.
    au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
    " Load indentation rules and plugins according to filetype
    filetype plugin indent on
endif

" Map ctrl+n to jump to next buffer, ctrl+p to previous buffer
nmap <C-P> :bp<CR>
nmap <C-N> :bn<CR>

" Functions for statusline. TODO: need to review this
function! CurDir()
    let curdir = substitute(getcwd(), '$HOME', "~/", "g")
    return curdir
endfunction
function! HasPaste()
    if &paste
        return 'PASTE MODE  '
    else
        return ''
    endif
endfunction

" Source the vimrc file after saving it
if has("autocmd")
  autocmd bufwritepost .vimrc source $MYVIMRC
endif
