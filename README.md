# 🚀 Arch Linux Installer with Hyprland

An automated, interactive installer for Arch Linux with Hyprland, personalized dotfiles, and a complete development environment.

<div align="center">

![Arch Linux](https://img.shields.io/badge/Arch%20Linux-1793D1?style=for-the-badge&logo=arch-linux&logoColor=white)
![Hyprland](https://img.shields.io/badge/Hyprland-00D9FF?style=for-the-badge&logo=wayland&logoColor=white)
![Neovim](https://img.shields.io/badge/Neovim-57A143?style=for-the-badge&logo=neovim&logoColor=white)
![tmux](https://img.shields.io/badge/tmux-1BB91F?style=for-the-badge&logo=tmux&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

</div>

## ✨ Features

- 📱 **Interactive TUI** - User-friendly installation wizard
- 🎨 **Hyprland Desktop** - Modern Wayland compositor
- ⚡ **Fully Automated** - From partitioning to development tools
- 🎭 **Pre-themed** - Catppuccin Mocha out of the box
- 💻 **Dev Ready** - Node.js, Bun, Neovim, and more

## 📦 What's Included

| Category      | Tools                                      |
| ------------- | ------------------------------------------ |
| **Desktop**   | Hyprland, Waybar, Wofi, SDDM               |
| **Terminal**  | Kitty, Ghostty, Zsh + oh-my-zsh            |
| **Editors**   | Neovim, Zed                                |
| **Dev Tools** | Git, Node.js (nvm), Bun, Lazygit           |
| **Utilities** | ripgrep, fzf, zoxide, btop, tmux           |
| **Apps**      | Discord, Zen Browser, Nautilus             |
| **Theme**     | Catppuccin Mocha, JetBrains Mono Nerd Font |

## 🚀 Installation

### Prerequisites

- Arch Linux ISO booted
- Internet connection
- Target disk (⚠️ **will be formatted!**)

### One-Line Install

```bash
curl -L https://raw.githubusercontent.com/armando-rios/dev-setup/main/install.sh | bash
```

The installer will guide you through:

1. System checks - Internet, UEFI detection
2. Disk setup - Selection and partitioning
3. Base install - Core system + bootloader
4. Software - Desktop environment + apps
5. Dotfiles - Personal configurations

## ⚠️ Important

- This will format your selected disk - all data will be lost
- Configured for AMD graphics (modify for NVIDIA/Intel)
- Uses dotfiles from armando-rios/dotfiles https://github.com/armando-rios/dotfiles

## 🛠️ Development

Test development branch:

curl -L https://raw.githubusercontent.com/armando-rios/dev-setup/dev/main/install.sh | INSTALLER_BRANCH=dev/branch-name bash

## 📄 License

[MIT License](LICENSE)

---

Built with Arch Linux https://archlinux.org/ • Hyprland https://hyprland.org/ • Catppuccin https://github.com/catppuccin/catppuccin
