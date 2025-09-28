#!/usr/bin/env python3
"""
Disk partitioning and formatting utilities
"""

import subprocess
import time
from .system import run_command


def is_iso_device(disk):
    """Check if disk is the current Arch ISO device"""
    print(f"Checking if {disk} is the ISO device...")
    
    # Check if any partition of this disk is mounted as archiso
    mount_output = run_command("mount | grep archiso", capture_output=True)
    if mount_output and disk in mount_output:
        print(f"WARNING: {disk} appears to be the Arch ISO device")
        return True
    
    # Check for ISO 9660 filesystem (common for ISO images)
    blkid_output = run_command(f"blkid {disk}*", capture_output=True)
    if blkid_output and ("iso9660" in blkid_output.lower() or "archiso" in blkid_output.lower()):
        print(f"WARNING: {disk} contains ISO filesystem")
        return True
    
    # Check if it's a removable device that might be the USB
    removable_check = run_command(f"cat /sys/block/{disk.split('/')[-1]}/removable 2>/dev/null", capture_output=True)
    if removable_check == "1":
        # It's removable, check size (USB sticks are usually smaller)
        size_output = run_command(f"lsblk -b -o SIZE -n {disk}", capture_output=True)
        if size_output:
            try:
                size_bytes = int(size_output.strip())
                size_gb = size_bytes / (1024**3)
                # Typical Arch ISO is around 1-2GB, USB sticks are often 4-32GB
                if size_gb < 64:  # Likely a USB stick
                    print(f"WARNING: {disk} is a small removable device ({size_gb:.1f}GB)")
                    return True
            except:
                pass
    
    return False


def get_safe_disks():
    """Get list of disks that are safe to use (not ISO device)"""
    from .system import get_available_disks
    
    all_disks = get_available_disks()
    safe_disks = []
    
    for disk in all_disks:
        if not is_iso_device(disk['name']):
            safe_disks.append(disk)
        else:
            print(f"Filtering out {disk['name']} - appears to be ISO device")
    
    return safe_disks


def cleanup_disk(disk):
    """Clean up disk before partitioning to avoid 'busy' errors"""
    print(f"Cleaning up disk: {disk}")
    
    # Safety check - don't clean the ISO device
    if is_iso_device(disk):
        print(f"ERROR: Refusing to clean {disk} - appears to be the ISO device!")
        return False
    
    # Step 1: Unmount any mounted partitions from this disk
    print("Unmounting any existing partitions...")
    run_command("swapoff -a", capture_output=False)  # Turn off swap
    run_command("umount -R /mnt", capture_output=False)  # Unmount recursively
    
    # Find and unmount any partitions from this disk
    mount_check = run_command("mount | grep " + disk, capture_output=True)
    if mount_check:
        print(f"Found mounted partitions: {mount_check}")
        # Unmount any partitions from this disk
        run_command(f"umount -f {disk}*", capture_output=False)
    
    # Step 2: Kill any processes using the disk
    print("Checking for processes using the disk...")
    run_command(f"fuser -km {disk}", capture_output=False)
    time.sleep(1)
    
    # Step 3: Clear filesystem signatures (only on partitions, not whole disk)
    print("Clearing partition signatures...")
    partitions = run_command(f"lsblk -ln -o NAME {disk} | grep -v '^{disk.split('/')[-1]}$'", capture_output=True)
    if partitions:
        for partition in partitions.strip().split('\n'):
            if partition.strip():
                partition_path = f"/dev/{partition.strip()}"
                run_command(f"wipefs -af {partition_path}", capture_output=False)
    
    # Step 4: Force kernel to re-read partition table
    print("Refreshing partition table...")
    run_command(f"partprobe {disk}", capture_output=False)
    run_command(f"blockdev --rereadpt {disk}", capture_output=False)
    
    # Step 5: Brief pause to let kernel settle
    time.sleep(2)
    print("Disk cleanup completed")
    return True


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
        if not run_command("mkdir -p /mnt/boot", capture_output=False):
            print("Failed to create EFI directory")
            return False
        
        print(f"Mounting EFI partition: {boot_partition}")
        if not run_command(f"mount {boot_partition} /mnt/boot", capture_output=False):
            print(f"Failed to mount EFI partition: {boot_partition}")
            return False
        print("EFI partition mounted successfully")
    
    return True


def generate_fstab():
    """Generate fstab for mounted system"""
    return run_command("genfstab -U /mnt >> /mnt/etc/fstab", capture_output=False)
