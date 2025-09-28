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
    
    for i, cmd in enumerate(commands, 1):
        print(f"Executing step {i}/{len(commands)}: {cmd}")
        result = run_command(cmd, capture_output=True)
        if result is None:
            print(f"Error executing: {cmd}")
            # Get detailed error
            error_result = run_command(f"{cmd} 2>&1", capture_output=True)
            print(f"Error details: {error_result}")
            return False
        print(f"Step {i} completed successfully")
    return True


def create_bios_partitions(disk):
    """Create BIOS partition scheme"""
    commands = [
        f"sgdisk --zap-all {disk}",
        f"sgdisk --new=1:0:+1M --typecode=1:ef02 --change-name=1:'BIOS boot' {disk}",
        f"sgdisk --new=2:0:0 --typecode=2:8300 --change-name=2:'Linux filesystem' {disk}"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"Executing step {i}/{len(commands)}: {cmd}")
        result = run_command(cmd, capture_output=True)
        if result is None:
            print(f"Error executing: {cmd}")
            # Get detailed error
            error_result = run_command(f"{cmd} 2>&1", capture_output=True)
            print(f"Error details: {error_result}")
            return False
        print(f"Step {i} completed successfully")
    return True


def get_partition_name(disk, partition_number):
    """Get correct partition name for different disk types"""
    if 'nvme' in disk or 'mmcblk' in disk:
        return f"{disk}p{partition_number}"
    else:
        return f"{disk}{partition_number}"


def format_partitions(disk, is_uefi):
    """Format partitions according to system type"""
    if is_uefi:
        boot_partition = get_partition_name(disk, 1)
        root_partition = get_partition_name(disk, 2)
        
        print(f"Formatting EFI partition: {boot_partition}")
        if not run_command(f"mkfs.fat -F32 {boot_partition}", capture_output=False):
            print(f"Failed to format EFI partition: {boot_partition}")
            return False
        print("EFI partition formatted successfully")
    else:
        root_partition = get_partition_name(disk, 2)
    
    print(f"Formatting root partition: {root_partition}")
    if not run_command(f"mkfs.ext4 -F {root_partition}", capture_output=False):
        print(f"Failed to format root partition: {root_partition}")
        return False
    print("Root partition formatted successfully")
    
    return True


def mount_partitions(disk, is_uefi):
    """Mount partitions to /mnt"""
    root_partition = get_partition_name(disk, 2)
    
    print(f"Mounting root partition: {root_partition}")
    if not run_command(f"mount {root_partition} /mnt", capture_output=False):
        print(f"Failed to mount root partition: {root_partition}")
        return False
    print("Root partition mounted successfully")
    
    if is_uefi:
        boot_partition = get_partition_name(disk, 1)
        print("Creating EFI mount point...")
        if not run_command("mkdir -p /mnt/boot/efi", capture_output=False):
            print("Failed to create EFI directory")
            return False
        
        print(f"Mounting EFI partition: {boot_partition}")
        if not run_command(f"mount {boot_partition} /mnt/boot/efi", capture_output=False):
            print(f"Failed to mount EFI partition: {boot_partition}")
            return False
        print("EFI partition mounted successfully")
    
    return True


def generate_fstab():
    """Generate fstab for mounted system"""
    return run_command("genfstab -U /mnt >> /mnt/etc/fstab", capture_output=False)