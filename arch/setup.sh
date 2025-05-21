#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
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
  sudo pacman -S --needed --noconfirm git base-devel nvm neovim ripgrep fzf gcc waybar hyprpaper hyprsunset swaync zsh ghostty lsd ttf-jetbrains-mono-nerd discord lazygit unzip steam
}

install_yay() {
  echo "Installing yay"
  git clone https://aur.archlinux.org/yay.git
  cd yay
  makepkg -si
}

install_homebrew() {
  echo "Installing Brew"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
}

install_aur_packages() {
  echo "Installing yay packages"
  yay -S --needed --noconfirm zen-browser-bin wshowkeys-mao-git hyprshot
  cd ~
}

clone_dotfiles() {
  echo "Cloning dotfiles"
  git clone https://github.com/armando-rios/dotfiles.git ~/.dotfiles
}

zsh_setup() {
  echo "Setting up zsh"
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
}

copy_dotfiles() {
  echo "Copying dotfiles"
  cp -r ~/.dotfiles/.config ~/.config
  cp -r ~/.dotfiles/.zshrc ~/.zshrc
  cp -r ~/.dotfiles/.tmux.conf ~/.tmux.conf
  cp -r ~/.dotfiles/.ssh/ ~/.ssh
}

install_nodejs() {
  echo "Installing nodejs"
  zsh
  nvm install node
  exit
}

echo "Running setup script"

run_step "Updating system" update_system

run_step "Installing packages" install_packages

run_step "Installing yay" install_yay

run_step "Installing yay packages" install_aur_packages

run_step "Cloning dotfiles" clone_dotfiles

run_step "Copying dotfiles" copy_dotfiles

run_step "Installing nodejs" install_nodejs

run_step "Setting up zsh" zsh_setup

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}Please restart your computer.${NC}"
