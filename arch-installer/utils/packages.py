#!/usr/bin/env python3
"""
Package definitions for Arch Linux installer
"""

# Essential packages organized by category
ESSENTIAL_PACKAGES = {
    'development': [
        'git',
        'base-devel',
        'gcc',
        'neovim',
        'ripgrep',
        'fzf',
        'lazygit',
        'unzip',
        'stow',
    ],
    
    'shell_terminal': [
        'zsh',
        'nvm',
        'lsd',
        'kitty',
        'zoxide',
    ],
    
    'wayland_hyprland': [
        'hyprland',
        'waybar',
        'hyprpaper',
        'hyprsunset',
        'swaync',
        'wofi',
    ],
    
    'system_services': [
        'sddm',
        'network-manager-applet',
        'wireless_tools',
        'seatd',
    ],
    
    'audio': [
        'pipewire',
        'pipewire-audio',
        'pipewire-pulse', 
        'wireplumber',
    ],
    
    'applications': [
        'ghostty',
        'discord',
        'zed',
        'nwg-look',
    ],
    
    'fonts': [
        'ttf-jetbrains-mono-nerd'
    ]
}

# Flatten all essential packages into a single list
ALL_ESSENTIAL_PACKAGES = []
for category_packages in ESSENTIAL_PACKAGES.values():
    ALL_ESSENTIAL_PACKAGES.extend(category_packages)

# AMD graphics drivers
AMD_GRAPHICS_PACKAGES = [
    'libva-mesa-driver',
    'mesa',
    'vulkan-radeon',
    'xf86-video-amdgpu',
    'xf86-video-ati',
    'xorg-server',
    'xorg-xinit'
]

# AUR packages
AUR_PACKAGES = [
    'zen-browser-bin',
    'wshowkeys-mao-git', 
    'hyprshot'
]

def get_packages_by_category(category):
    """Get packages for a specific category"""
    return ESSENTIAL_PACKAGES.get(category, [])

def get_all_essential_packages():
    """Get all essential packages as a flat list"""
    return ALL_ESSENTIAL_PACKAGES.copy()

def get_amd_graphics_packages():
    """Get AMD graphics driver packages"""
    return AMD_GRAPHICS_PACKAGES.copy()

def get_aur_packages():
    """Get AUR packages"""
    return AUR_PACKAGES.copy()