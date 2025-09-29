#!/usr/bin/env python3
"""
Input validation utilities for Arch Linux installer
"""

import re


def validate_hostname(hostname):
    """Validate hostname according to RFC standards"""
    if not hostname:
        return False, "Hostname cannot be empty"
    
    if len(hostname) > 63:
        return False, "Hostname must be 63 characters or less"
    
    if hostname.startswith('-') or hostname.endswith('-'):
        return False, "Hostname cannot start or end with hyphen"
    
    # Only allow alphanumeric characters and hyphens
    if not re.match(r'^[a-zA-Z0-9-]+$', hostname):
        return False, "Hostname can only contain letters, numbers, and hyphens"
    
    return True, ""


def validate_username(username):
    """Validate username according to Linux standards"""
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) > 32:
        return False, "Username must be 32 characters or less"
    
    if username.startswith('-') or username[0].isdigit():
        return False, "Username cannot start with hyphen or number"
    
    # Only allow lowercase letters, numbers, underscores, and hyphens
    if not re.match(r'^[a-z0-9_-]+$', username):
        return False, "Username can only contain lowercase letters, numbers, underscores, and hyphens"
    
    # Check for reserved usernames
    reserved = ['root', 'bin', 'daemon', 'adm', 'lp', 'sync', 'shutdown', 'halt', 'mail']
    if username in reserved:
        return False, f"Username '{username}' is reserved"
    
    return True, ""


def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Optional: Add more password strength requirements
    # if not re.search(r'[A-Z]', password):
    #     return False, "Password must contain at least one uppercase letter"
    
    return True, ""


def validate_timezone(timezone):
    """Validate timezone format"""
    if not timezone:
        return False, "Timezone cannot be empty"
    
    # Basic timezone format validation (e.g., "America/New_York")
    if not re.match(r'^[A-Za-z_]+/[A-Za-z_]+$', timezone):
        return False, "Timezone must be in format 'Region/City' (e.g., 'America/New_York')"
    
    return True, ""


def validate_locale(locale):
    """Validate locale format"""
    if not locale:
        return False, "Locale cannot be empty"
    
    # Basic locale format validation (e.g., "en_US.UTF-8")
    if not re.match(r'^[a-z]{2}_[A-Z]{2}\.UTF-8$', locale):
        return False, "Locale must be in format 'xx_YY.UTF-8' (e.g., 'en_US.UTF-8')"
    
    return True, ""


def validate_disk_path(disk_path):
    """Validate disk path format"""
    if not disk_path:
        return False, "Disk path cannot be empty"
    
    if not disk_path.startswith('/dev/'):
        return False, "Disk path must start with '/dev/'"
    
    return True, ""