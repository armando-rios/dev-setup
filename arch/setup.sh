#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' # No Color

run_step() {
  local message="$1"
  local function_name="$2"

  echo -e "${GREEN}==> $message${NC}"
  sleep 1
  $function_name
  sleep 1
  clear
}

update_system() {
  echo "Updating system"
  sudo pacman -Syu --noconfirm
}

install_packages() {
  echo "Installing packages"
  sudo pacman -S --needed --noconfirm git base-devel nvm neovim ripgrep fzf gcc waybar hyprpaper hyprsunset swaync zsh ghostty discord lazygit steam
}

install_yay() {
  echo "Installing yay"
  git clone https://aur.archlinux.org/yay.git
  cd yay
  makepkg -si
}

install_aur_packages() {
  echo "Installing yay packages"
  yay -S --needed --noconfirm zen-browser-bin wshowkeys-mao-git hyprshot
}

clone_dotfiles() {
  echo "Cloning dotfiles"
  git clone https://github.com/armando-rios/dotfiles.git ~/.dotfiles
}

copy_dotfiles() {
  echo "Copying dotfiles"
  cp -r ~/.dotfiles/.config ~/.config
  cp -r ~/.dotfiles/.zshrc ~/.zshrc
  cp -r ~/.dotfiles/.tmux.conf ~/.tmux.conf
  cp -r ~/.dotfiles/.ssh/ ~/.ssh
}

zsh_setup() {
  echo "Setting up zsh"
  sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
}

install_nodejs() {
  echo "Installing nodejs"
  nvm install node
}

zsh_setup() {
  echo "Setting up zsh"
  sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
}

