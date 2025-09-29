#!/usr/bin/env python3
"""
Dotfiles and development environment setup utilities
"""

from .chroot import chroot_command
from .system import run_command


def clone_dotfiles(username):
    """Clone dotfiles repository (exactamente como en setup.sh)"""
    print("Cloning dotfiles...")
    
    # Clonar dotfiles como usuario
    clone_cmd = f"sudo -u {username} git clone https://github.com/armando-rios/dotfiles.git /home/{username}/.dotfiles"
    if not chroot_command(clone_cmd):
        print("Failed to clone dotfiles repository")
        return False
    
    print("Dotfiles cloned successfully")
    return True


def setup_symbolic_links(username):
    """Create symbolic links for dotfiles using stow (exactamente como en setup.sh)"""
    print("Creating symbolic links for dotfiles...")
    
    # Cambiar al directorio de dotfiles
    cd_cmd = f"sudo -u {username} bash -c 'cd /home/{username}/.dotfiles'"
    
    # Eliminar archivos y directorios que van a ser reemplazados por dotfiles
    print("Removing conflicting default config files and directories...")
    remove_cmd = f"""sudo -u {username} bash -c '
        rm -rf /home/{username}/.config/alacritty 
        rm -rf /home/{username}/.config/ghostty 
        rm -rf /home/{username}/.config/hypr 
        rm -rf /home/{username}/.config/kitty 
        rm -rf /home/{username}/.config/nvim 
        rm -rf /home/{username}/.config/ohmyposh 
        rm -rf /home/{username}/.config/posting 
        rm -rf /home/{username}/.config/waybar 
        rm -rf /home/{username}/.config/wofi 
        rm -rf /home/{username}/.config/zed
        rm -f /home/{username}/.zshrc 
        rm -f /home/{username}/.tmux.conf
        rm -rf /home/{username}/.ssh
    '"""
    
    if not chroot_command(remove_cmd):
        print("Warning: Failed to remove some conflicting files")
    
    # Crear enlaces simbólicos con stow
    print("Creating symbolic links with stow...")
    stow_cmd = f"sudo -u {username} bash -c 'cd /home/{username}/.dotfiles && stow .'"
    if not chroot_command(stow_cmd):
        print("Failed to create symbolic links with stow")
        return False
    
    print("Symbolic links created successfully")
    return True


def install_nodejs_with_nvm(username):
    """Install Node.js with nvm (exactamente como en setup.sh)"""
    print("Installing Node.js with nvm...")
    
    # Usar zsh con dotfiles ya aplicados que incluyen nvm
    # Esto requiere que los dotfiles ya estén aplicados con la configuración de nvm
    nodejs_cmd = f"""sudo -u {username} zsh -c 'source /home/{username}/.zshrc && nvm install --lts && nvm use --lts'"""
    
    if not chroot_command(nodejs_cmd):
        print("Failed to install Node.js with nvm")
        return False
    
    print("Node.js installed successfully with nvm")
    return True


def install_bun(username):
    """Install Bun.js (exactamente como en setup.sh)"""
    print("Installing Bun.js...")
    
    # Instalar bun
    bun_cmd = f"sudo -u {username} bash -c 'curl -fsSL https://bun.sh/install | bash'"
    if not chroot_command(bun_cmd):
        print("Failed to install Bun.js")
        return False
    
    print("Bun.js installed successfully")
    return True


def phase4_dotfiles_and_development(username):
    """Complete Phase 4: Dotfiles and development environment setup"""
    print("=== Phase 4: Dotfiles and Development Environment ===")
    
    steps = [
        ("Cloning dotfiles repository", lambda: clone_dotfiles(username)),
        ("Setting up symbolic links with stow", lambda: setup_symbolic_links(username)),
        ("Installing Node.js with nvm", lambda: install_nodejs_with_nvm(username)),
        ("Installing Bun.js", lambda: install_bun(username))
    ]
    
    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        if not step_func():
            print(f"ERROR: Failed at step: {step_name}")
            return False
        print(f"✓ {step_name} completed successfully")
    
    print("\n=== Phase 4 completed successfully! ===")
    return True