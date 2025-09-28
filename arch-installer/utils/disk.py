#!/usr/bin/env python3
"""
Disk partitioning and formatting utilities
"""

import subprocess
from .system import run_command


def create_uefi_partitions(disk):
    """Create UEFI partition scheme"""
    commands = [
        f"sgdisk --zap-all {disk}",
        f"sgdisk --new=1:0:+1G --typecode=1:ef00 --change-name=1:'EFI System' {disk}",
        f"sgdisk --new=2:0:0 --typecode=2:8300 --change-name=2:'Linux filesystem' {disk}"
    ]
    
    for cmd in commands:
        if not run_command(cmd, capture_output=False):
            return False
    return True


def create_bios_partitions(disk):
    """Create BIOS partition scheme"""
    commands = [
        f"sgdisk --zap-all {disk}",
        f"sgdisk --new=1:0:+1M --typecode=1:ef02 --change-name=1:'BIOS boot' {disk}",
        f"sgdisk --new=2:0:0 --typecode=2:8300 --change-name=2:'Linux filesystem' {disk}"
    ]
    
    for cmd in commands:
        if not run_command(cmd, capture_output=False):
            return False
    return True


def format_partitions(disk, is_uefi):
    """Format partitions according to system type"""
    if is_uefi:
        boot_partition = f"{disk}1"
        root_partition = f"{disk}2"
        
        # Format EFI partition
        if not run_command(f"mkfs.fat -F32 {boot_partition}", capture_output=False):
            return False
    else:
        root_partition = f"{disk}2"
    
    # Format root partition
    if not run_command(f"mkfs.ext4 {root_partition}", capture_output=False):
        return False
    
    return True


def mount_partitions(disk, is_uefi):
    """Mount partitions to /mnt"""
    root_partition = f"{disk}2"
    
    # Mount root
    if not run_command(f"mount {root_partition} /mnt", capture_output=False):
        return False
    
    if is_uefi:
        boot_partition = f"{disk}1"
        # Create and mount EFI directory
        if not run_command("mkdir -p /mnt/boot/efi", capture_output=False):
            return False
        if not run_command(f"mount {boot_partition} /mnt/boot/efi", capture_output=False):
            return False
    
    return True


def generate_fstab():
    """Generate fstab for mounted system"""
    return run_command("genfstab -U /mnt >> /mnt/etc/fstab", capture_output=False)