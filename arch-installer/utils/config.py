#!/usr/bin/env python3
"""
Configuration constants for Arch Linux installer
"""

# System paths
CHROOT_PATH = "/mnt"
BOOT_PATH = "/boot"
HOME_PATH_TEMPLATE = "/home/{username}"

# Command flags
PACMAN_FLAGS = "--needed --noconfirm"
YAY_FLAGS = "-S --needed --noconfirm"
MAKEPKG_FLAGS = "-si --noconfirm"

# Git repositories
OH_MY_ZSH_REPO = "https://github.com/ohmyzsh/ohmyzsh"
YAY_REPO = "https://aur.archlinux.org/yay.git"

# Default system configuration
DEFAULT_LOCALE = "en_US.UTF-8"
DEFAULT_TIMEZONE = "America/New_York"
DEFAULT_HOSTNAME = "arch"
DEFAULT_USERNAME = "user"

# Service names
SYSTEM_SERVICES = [
    'sddm',           # Display manager
    'NetworkManager', # Network management  
    'seatd'           # Session management
]

# Sudo configuration
WHEEL_SUDO_LINE = "# %wheel ALL=(ALL:ALL) ALL"
WHEEL_SUDO_REPLACEMENT = "%wheel ALL=(ALL:ALL) ALL"
WHEEL_NOPASSWD_LINE = "%wheel ALL=(ALL:ALL) NOPASSWD: /usr/bin/pacman, /usr/bin/makepkg"