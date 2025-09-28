#!/usr/bin/env python3
"""
System validation and detection utilities
"""

import os
import subprocess
import urllib.request


def check_internet_connection():
    """Check if internet connection is available"""
    try:
        urllib.request.urlopen('http://archlinux.org', timeout=5)
        return True
    except:
        return False


def is_uefi():
    """Check if system is UEFI or BIOS"""
    return os.path.exists('/sys/firmware/efi')


def sync_clock():
    """Synchronize system clock with NTP"""
    try:
        subprocess.run(['timedatectl', 'set-ntp', 'true'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def run_command(command, capture_output=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            check=True
        )
        return result.stdout.strip() if capture_output else True
    except subprocess.CalledProcessError as e:
        return None


def get_available_disks():
    """Get list of available disks"""
    output = run_command("lsblk -dpno NAME,SIZE,MODEL | grep -v loop")
    if not output:
        return []
    
    disks = []
    for line in output.split('\n'):
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                size = parts[1]
                model = ' '.join(parts[2:]) if len(parts) > 2 else 'Unknown'
                disks.append({'name': name, 'size': size, 'model': model})
    
    return disks