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

enable_multilib() {
  echo "Checking multilib repository"
  if ! grep -q "^\[multilib\]" /etc/pacman.conf; then
    echo "Enabling multilib repository for Steam support"
    sudo sed -i '/^#\[multilib\]/,/^#Include.*multilib/ s/^#//' /etc/pacman.conf
    sudo pacman -Sy --noconfirm
    echo "Multilib repository enabled"
  else
    echo "Multilib repository already enabled"
  fi
}

update_system() {
  echo "Updating system"
  sudo pacman -Syu --noconfirm
}

install_packages() {
  echo "Installing packages"
  sudo pacman -S --needed --noconfirm git base-devel nvm neovim ripgrep fzf gcc waybar hyprpaper hyprsunset swaync zsh ghostty lsd ttf-jetbrains-mono-nerd discord lazygit unzip stow
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
  cd ~
}

clone_dotfiles() {
  echo "Cloning dotfiles"
  git clone https://github.com/armando-rios/dotfiles.git ~/.dotfiles
}

# function create simbolic links for the dotfiles
simbolic_link_dotfiles() {
  echo "Creating symbolic links for dotfiles"
  cd ~/.dotfiles
  
  # Eliminar archivos y directorios que van a ser reemplazados por dotfiles
  echo "Removing conflicting default config files and directories"
  rm -rf ~/.config/alacritty ~/.config/ghostty ~/.config/hypr ~/.config/kitty ~/.config/nvim ~/.config/ohmyposh ~/.config/posting ~/.config/waybar ~/.config/wofi ~/.config/zed
  rm -f ~/.zshrc ~/.tmux.conf
  rm -rf ~/.ssh
  
  # Crear enlaces simbólicos con stow
  stow .
  
  cd ~
}

copy_dotfiles() {
  echo "Copying dotfiles"
  cp -r ~/.dotfiles/.config ~/
  cp -r ~/.dotfiles/.zshrc ~/
  cp -r ~/.dotfiles/.tmux.conf ~/
  cp -r ~/.dotfiles/.ssh/ ~/
}

install_bun() {
  echo "Installing bun in a new zsh terminal"
  curl -fsSL https://bun.sh/install | bash
}

install_nodejs() {
  echo "Installing nodejs with nvm (from dotfiles config)"
  # Usar zsh con dotfiles ya aplicados que incluyen nvm
  zsh -c "source ~/.zshrc && nvm install --lts && nvm use --lts"
}

zsh_setup() {
  echo "Setting up zsh"
  git clone https://github.com/ohmyzsh/ohmyzsh ~/.oh-my-zsh
  chsh -s $(which zsh)
}

echo "Running setup script"

run_step "Updating system" update_system

run_step "Installing packages" install_packages

run_step "Installing yay" install_yay

run_step "Installing yay packages" install_aur_packages

run_step "Cloning dotfiles" clone_dotfiles

# run_step "Copying dotfiles" copy_dotfiles

run_step "Creating symbolic links for dotfiles" simbolic_link_dotfiles

run_step "Setting up zsh" zsh_setup

run_step "Installing bun" install_bun

run_step "Installing nodejs" install_nodejs

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}Please restart your computer.${NC}"
