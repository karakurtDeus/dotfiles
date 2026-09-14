# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

#
# ~/.zshrc
#

# editor
export EDITOR=nvim
export VISUAL=nvim

# aliases
alias ls='eza -lah --icons --group-directories-first --time-style=long-iso'
alias cat='bat'
alias grep='grep --color=auto'

# plagins
source ~/.config/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/.config/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source /usr/share/fzf/key-bindings.zsh
source /usr/share/fzf/completion.zsh

# history
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

setopt appendhistory
setopt sharehistory
setopt hist_ignore_dups

# completion
autoload -Uz compinit
compinit

# useful options
setopt autocd
setopt interactivecomments

# Powerlevel10k
source ~/.config/zsh/powerlevel10k/powerlevel10k.zsh-theme

function y() {
    local tmp="$(mktemp -t "yazi-cwd.XXXXXX")"

    yazi "$@" --cwd-file="$tmp"

    if cwd="$(cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
        builtin cd -- "$cwd"
    fi

    rm -f -- "$tmp"
}

# p10k config
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
