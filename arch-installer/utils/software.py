#!/usr/bin/env python3
"""
Software installation and configuration utilities for Arch Linux
"""

from .chroot import chroot_command
from .system import run_command


def install_packages(packages, use_aur=False, username=None):
    """Install packages using pacman or yay"""
    if isinstance(packages, str):
        packages = [packages]
    
    packages_str = ' '.join(packages)
    
    if use_aur:
        # Use yay for AUR packages
        cmd = f"sudo -u {username} yay -S --needed --noconfirm {packages_str}"
        return chroot_command(cmd)
    else:
        # Use pacman for official packages
        cmd = f"pacman -S --needed --noconfirm {packages_str}"
        return chroot_command(cmd)


def install_essential_packages():
    """Install essential packages organized by category"""
    print("Installing essential packages...")
    
    essential_packages = [
        # Development tools
        'git',
        'base-devel',
        'gcc',
        'neovim',
        'ripgrep',
        'fzf',
        'lazygit',
        'unzip',
        'stow',
        
        # Shell and terminal
        'zsh',
        'nvm',
        'lsd',
        'kitty',
        'zoxide',
        
        # Wayland/Hyprland
        'hyprland',
        'waybar',
        'hyprpaper',
        'hyprsunset',
        'swaync',
        'wofi',
        
        # System services
        'sddm',
        'network-manager-applet',
        'wireless_tools',
        'seatd',
        
        # Audio
        'pipewire',
        'pipewire-audio',
        'pipewire-pulse', 
        'wireplumber',
        
        # Applications
        'ghostty',
        'discord',
        'zed',
        'nwg-look',
        
        # Fonts
        'ttf-jetbrains-mono-nerd'
    ]
    
    return install_packages(essential_packages)


def install_amd_graphics_drivers():
    """Install AMD graphics drivers"""
    print("Installing AMD graphics drivers...")
    
    amd_packages = [
        'libva-mesa-driver',
        'mesa',
        'vulkan-radeon',
        'xf86-video-amdgpu',
        'xf86-video-ati',
        'xorg-server',
        'xorg-xinit'
    ]
    
    return install_packages(amd_packages)


def setup_aur_helper(username):
    """Install and configure yay AUR helper"""
    print("Setting up yay AUR helper...")
    
    # Ensure git and base-devel are installed first
    if not install_packages(['git', 'base-devel']):
        print("Failed to install git and base-devel")
        return False
    
    # Limpiar instalación previa si existe
    chroot_command(f"rm -rf /home/{username}/yay")
    
    # Clone and compile yay
    print("Cloning yay repository...")
    if not chroot_command(f"sudo -u {username} git clone https://aur.archlinux.org/yay.git /home/{username}/yay"):
        print("Failed to clone yay repository")
        return False
    
    # Build and install yay
    print("Building and installing yay...")
    build_cmd = f'sudo -u {username} bash -c "cd /home/{username}/yay && makepkg -si --noconfirm"'
    if not chroot_command(build_cmd):
        print("Failed to build yay")
        return False
    
    # Limpiar directorio temporal
    chroot_command(f"rm -rf /home/{username}/yay")
    
    print("yay AUR helper installed successfully")
    return True


def install_aur_packages(username):
    """Install AUR packages"""
    print("Installing AUR packages...")
    
    aur_packages = [
        'zen-browser-bin',
        'wshowkeys-mao-git', 
        'hyprshot'
    ]
    
    return install_packages(aur_packages, use_aur=True, username=username)


def install_ohmyzsh(username):
    """Install oh-my-zsh"""
    print("Installing oh-my-zsh...")
    
    # Clone oh-my-zsh repository
    omz_cmd = f"sudo -u {username} git clone https://github.com/ohmyzsh/ohmyzsh /home/{username}/.oh-my-zsh"
    if not chroot_command(omz_cmd):
        print("Failed to install oh-my-zsh")
        return False
    
    print("oh-my-zsh installed successfully")
    return True


def change_shell_to_zsh(username):
    """Change default shell to zsh"""
    print("Changing default shell to zsh...")
    
    if not chroot_command(f"chsh -s $(which zsh) {username}"):
        print(f"Failed to change shell for {username}")
        return False
    
    print("Shell changed to zsh")
    return True


def enable_services():
    """Enable necessary system services"""
    print("Enabling system services...")
    
    services = [
        'sddm',           # Display manager
        'NetworkManager', # Network management  
        'seatd'           # Session management
    ]
    
    for service in services:
        print(f"Enabling {service}...")
        if not chroot_command(f"systemctl enable {service}"):
            print(f"Failed to enable {service}")
            return False
    
    print("All services enabled successfully")
    return True


def phase3_install_essential_software(username):
    """Complete Phase 3: Install essential software"""
    print("=== Phase 3: Installing Essential Software ===")
    
    steps = [
        ("Installing essential packages", install_essential_packages),
        ("Installing AMD graphics drivers", install_amd_graphics_drivers),
        ("Setting up AUR helper (yay)", lambda: setup_aur_helper(username)),
        ("Installing AUR packages", lambda: install_aur_packages(username)),
        ("Installing oh-my-zsh", lambda: install_ohmyzsh(username)),
        ("Changing shell to zsh", lambda: change_shell_to_zsh(username)),
        ("Enabling system services", enable_services)
    ]
    
    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        if not step_func():
            print(f"ERROR: Failed at step: {step_name}")
            return False
        print(f"✓ {step_name} completed successfully")
    
    print("\n=== Phase 3 completed successfully! ===")
    return True
