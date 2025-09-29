#!/usr/bin/env python3
"""
Chroot utilities for system configuration
"""

import subprocess
from .system import run_command


def chroot_command(command):
    """Execute command in chroot environment"""
    chroot_cmd = f"arch-chroot /mnt {command}"
    print(f"CHROOT: {chroot_cmd}")
    result = run_command(chroot_cmd, capture_output=False)
    if result:
        print("CHROOT: Command completed successfully")
    else:
        print("CHROOT: Command failed")
    return result


def setup_timezone(timezone):
    """Configure system timezone"""
    print(f"Setting timezone to: {timezone}")
    
    # Set timezone
    if not chroot_command(f"ln -sf /usr/share/zoneinfo/{timezone} /etc/localtime"):
        return False
    
    # Set hardware clock
    if not chroot_command("hwclock --systohc"):
        return False
    
    print("Timezone configured successfully")
    return True


def setup_locales(locale):
    """Configure system locales"""
    print(f"Setting up locale: {locale}")
    
    # Uncomment locale in locale.gen
    sed_cmd = f"sed -i 's/#{locale}/{locale}/' /etc/locale.gen"
    if not chroot_command(sed_cmd):
        print("Failed to edit locale.gen")
        return False
    
    # Also enable en_US.UTF-8 as fallback
    if locale != "en_US.UTF-8":
        fallback_cmd = "sed -i 's/#en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen"
        if not chroot_command(fallback_cmd):
            print("Failed to enable en_US.UTF-8 fallback")
            return False
    
    # Generate locales
    if not chroot_command("locale-gen"):
        print("Failed to generate locales")
        return False
    
    # Set LANG variable
    if not chroot_command(f"bash -c \"echo 'LANG={locale}' > /etc/locale.conf\""):
        print("Failed to set LANG in locale.conf")
        return False
    
    print("Locales configured successfully")
    return True


def setup_hostname(hostname):
    """Configure system hostname"""
    print(f"Setting hostname: {hostname}")
    
    # Set hostname
    if not chroot_command(f"bash -c \"echo '{hostname}' > /etc/hostname\""):
        print("Failed to set hostname")
        return False
    
    # Configure hosts file
    hosts_content = f"""127.0.0.1	localhost
::1		localhost
127.0.1.1	{hostname}.localdomain	{hostname}"""
    
    hosts_cmd = f"bash -c \"cat > /etc/hosts << 'EOF'\n{hosts_content}\nEOF\""
    if not chroot_command(hosts_cmd):
        print("Failed to configure hosts file")
        return False
    
    print("Hostname configured successfully")
    return True


def setup_network():
    """Enable network services"""
    print("Configuring network services...")
    
    # Enable NetworkManager
    if not chroot_command("systemctl enable NetworkManager"):
        print("Failed to enable NetworkManager")
        return False
    
    print("Network services configured successfully")
    return True


def setup_users(username, root_password, user_password):
    """Configure root password and create user"""
    print("Setting up users...")
    
    # Set root password
    print("Setting root password...")
    cmd = f"bash -c \"echo 'root:{root_password}' | chpasswd\""
    print(f"Executing: {cmd}")
    if not chroot_command(cmd):
        print("ERROR: Failed to set root password")
        return False
    print("Root password set successfully")
    
    # Create user
    print(f"Creating user: {username}")
    cmd = f"useradd -m -G wheel,audio,video,optical,storage -s /bin/bash {username}"
    print(f"Executing: {cmd}")
    if not chroot_command(cmd):
        print(f"ERROR: Failed to create user: {username}")
        return False
    print(f"User {username} created successfully")
    
    # Set user password
    print(f"Setting password for user: {username}")
    cmd = f"bash -c \"echo '{username}:{user_password}' | chpasswd\""
    print(f"Executing: {cmd}")
    if not chroot_command(cmd):
        print(f"ERROR: Failed to set password for user: {username}")
        return False
    print(f"Password for {username} set successfully")
    
    # Configure sudo
    print("Configuring sudo access...")
    sudo_cmd = "sed -i 's/# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers"
    if not chroot_command(sudo_cmd):
        print("Failed to configure sudo")
        return False
    
    # Add NOPASSWD for AUR installation (pacman and makepkg)
    print("Configuring NOPASSWD for AUR installation...")
    nopasswd_cmd = 'bash -c "echo \'%wheel ALL=(ALL:ALL) NOPASSWD: /usr/bin/pacman, /usr/bin/makepkg\' >> /etc/sudoers"'
    if not chroot_command(nopasswd_cmd):
        print("Failed to configure NOPASSWD")
        return False
    
    print("Users configured successfully")
    return True


def setup_bootloader(is_uefi, disk_path=None):
    """Install and configure GRUB bootloader"""
    print("Setting up GRUB bootloader...")
    
    if is_uefi:
        print("Configuring GRUB for UEFI...")
        
        # Install GRUB for UEFI
        grub_install_cmd = "grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB"
        if not chroot_command(grub_install_cmd):
            print("Failed to install GRUB for UEFI")
            return False
    else:
        print("Configuring GRUB for BIOS...")
        
        if not disk_path:
            print("Error: disk path required for BIOS installation")
            return False
        
        # Install GRUB for BIOS
        grub_install_cmd = f"grub-install --target=i386-pc {disk_path}"
        if not chroot_command(grub_install_cmd):
            print("Failed to install GRUB for BIOS")
            return False
    
    # Generate GRUB configuration
    print("Generating GRUB configuration...")
    if not chroot_command("grub-mkconfig -o /boot/grub/grub.cfg"):
        print("Failed to generate GRUB configuration")
        return False
    
    print("GRUB bootloader configured successfully")
    return True