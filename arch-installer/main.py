#!/usr/bin/env python3
"""
Arch Linux Installer with Hyprland
Entry point for the installation system
"""

import sys
import time
from utils.system import check_internet_connection, is_uefi, sync_clock, get_available_disks, run_command
from utils.disk import create_uefi_partitions, create_bios_partitions, format_partitions, mount_partitions, generate_fstab
from utils.chroot import setup_timezone, setup_locales, setup_hostname, setup_network, setup_users, setup_bootloader
from utils.tui import TUI


class ArchInstaller:
    def __init__(self):
        self.config = {}
        self.tui = TUI()
    
    def welcome_screen(self):
        """Show welcome screen and initial checks"""
        lines = [
            "Welcome to Arch Linux Installer!",
            "",
            "🎯 This installer will guide you through setting up Arch Linux with Hyprland",
            "📝 Features:",
            "  • Interactive menu navigation",
            "  • Automatic system detection", 
            "  • Step-by-step installation process",
            "  • Hyprland desktop environment setup",
            "",
            "⚠️  WARNING: This will format your selected disk!"
        ]
        
        self.tui.show_info_screen("Welcome", lines, step=1, total_steps=6)
        
        if not self.tui.show_confirmation("Start Installation", 
                                        "Are you ready to begin the installation?", 
                                        default=True):
            return False
        return True
    
    def system_checks(self):
        """Perform initial system checks"""
        steps = [
            ("Checking internet connection...", "current"),
            ("Synchronizing system clock...", "pending"),
            ("Detecting system type...", "pending")
        ]
        
        self.tui.show_progress("System Checks", steps, step=2, total_steps=6)
        time.sleep(1)
        
        # Check internet
        if not check_internet_connection():
            steps[0] = ("Internet connection check", "error")
            self.tui.show_progress("System Checks", steps, step=2, total_steps=6)
            self.tui.show_info_screen("Error", ["ERROR: No internet connection detected!",
                                               "Please connect to the internet and try again."], 
                                    step=2, total_steps=6)
            return False
        
        steps[0] = ("Internet connection verified", "completed")
        steps[1] = ("Synchronizing system clock...", "current")
        self.tui.show_progress("System Checks", steps, step=2, total_steps=6)
        time.sleep(1)
        
        # Sync clock
        if sync_clock():
            steps[1] = ("System clock synchronized", "completed")
        else:
            steps[1] = ("Clock sync failed (continuing anyway)", "completed")
        
        steps[2] = ("Detecting system type...", "current")
        self.tui.show_progress("System Checks", steps, step=2, total_steps=6)
        time.sleep(1)
        
        # Detect system type
        self.config['uefi'] = is_uefi()
        system_type = "UEFI" if self.config['uefi'] else "BIOS"
        steps[2] = (f"System type detected: {system_type}", "completed")
        
        self.tui.show_progress("System Checks", steps, step=2, total_steps=6)
        time.sleep(1)
        
        return True
    
    def select_disk(self):
        """Let user select installation disk"""
        disks = get_available_disks()
        if not disks:
            self.tui.show_info_screen("Error", ["ERROR: No disks found!"], step=3, total_steps=6)
            return False
        
        disk_options = [f"{disk['name']} - {disk['size']} ({disk['model']})" for disk in disks]
        
        choice = self.tui.show_menu("Disk Selection", disk_options, step=3, total_steps=6)
        if choice == -1:
            return False
        
        self.config['disk'] = disks[choice]['name']
        
        # Confirm disk selection
        if not self.tui.show_confirmation("Confirm Disk Selection", 
                                        f"Selected disk: {self.config['disk']}\n\n"
                                        "⚠️  ALL DATA on this disk will be PERMANENTLY ERASED!\n\n"
                                        "Are you absolutely sure?", 
                                        default=False):
            return False
        
        return True
    
    def basic_config(self):
        """Get basic system configuration"""
        # Hostname
        self.config['hostname'] = self.tui.show_text_input("System Configuration", 
                                                          "Enter hostname:", 
                                                          default="arch",
                                                          step=4, total_steps=6)
        if not self.config['hostname']:
            return False
        
        # Username
        self.config['username'] = self.tui.show_text_input("System Configuration", 
                                                          "Enter username:", 
                                                          default="user",
                                                          step=4, total_steps=6)
        if not self.config['username']:
            return False
        
        # Timezone
        timezone_options = [
            "America/New_York (Eastern)",
            "America/Chicago (Central)", 
            "America/Denver (Mountain)",
            "America/Los_Angeles (Pacific)",
            "Europe/London",
            "Europe/Berlin",
            "Asia/Tokyo",
            "Custom timezone"
        ]
        
        tz_choice = self.tui.show_menu("Select Timezone", timezone_options, step=4, total_steps=6)
        if tz_choice == -1:
            return False
        
        if tz_choice == len(timezone_options) - 1:  # Custom
            self.config['timezone'] = self.tui.show_text_input("Custom Timezone", 
                                                              "Enter timezone (e.g., Europe/Madrid):", 
                                                              step=4, total_steps=6)
        else:
            tz_map = [
                "America/New_York", "America/Chicago", "America/Denver", 
                "America/Los_Angeles", "Europe/London", "Europe/Berlin", "Asia/Tokyo"
            ]
            self.config['timezone'] = tz_map[tz_choice]
        
        # Locale
        locale_options = [
            "en_US.UTF-8 (English - US)",
            "en_GB.UTF-8 (English - UK)", 
            "es_ES.UTF-8 (Spanish - Spain)",
            "es_MX.UTF-8 (Spanish - Mexico)",
            "Custom locale"
        ]
        
        locale_choice = self.tui.show_menu("Select Locale", locale_options, step=4, total_steps=6)
        if locale_choice == -1:
            return False
        
        if locale_choice == len(locale_options) - 1:  # Custom
            self.config['locale'] = self.tui.show_text_input("Custom Locale", 
                                                            "Enter locale (e.g., de_DE.UTF-8):", 
                                                            step=4, total_steps=6)
        else:
            locale_map = ["en_US.UTF-8", "en_GB.UTF-8", "es_ES.UTF-8", "es_MX.UTF-8"]
            self.config['locale'] = locale_map[locale_choice]
        
        # Root password
        while True:
            self.config['root_password'] = self.tui.show_password_input("Security Configuration", 
                                                                       "Enter root password:", 
                                                                       step=4, total_steps=6)
            if self.config['root_password']:
                # Confirm password
                confirm_password = self.tui.show_password_input("Security Configuration", 
                                                               "Confirm root password:", 
                                                               step=4, total_steps=6)
                if self.config['root_password'] == confirm_password:
                    break
                else:
                    self.tui.show_info_screen("Password Mismatch", 
                                            ["ERROR: Passwords do not match!", 
                                             "Please try again."], 
                                            step=4, total_steps=6)
            else:
                self.tui.show_info_screen("Password Required", 
                                        ["ERROR: Root password is required!", 
                                         "Please enter a password."], 
                                        step=4, total_steps=6)
        
        # User password
        while True:
            self.config['user_password'] = self.tui.show_password_input("Security Configuration", 
                                                                       f"Enter password for {self.config['username']}:", 
                                                                       step=4, total_steps=6)
            if self.config['user_password']:
                # Confirm password
                confirm_password = self.tui.show_password_input("Security Configuration", 
                                                               f"Confirm password for {self.config['username']}:", 
                                                               step=4, total_steps=6)
                if self.config['user_password'] == confirm_password:
                    break
                else:
                    self.tui.show_info_screen("Password Mismatch", 
                                            ["ERROR: Passwords do not match!", 
                                             "Please try again."], 
                                            step=4, total_steps=6)
            else:
                self.tui.show_info_screen("Password Required", 
                                        ["ERROR: User password is required!", 
                                         "Please enter a password."], 
                                        step=4, total_steps=6)
        
        return True
    
    def installation_summary(self):
        """Show installation summary and confirm"""
        return self.tui.show_summary("Installation Summary", self.config, step=5, total_steps=6)
    
    def install_system(self):
        """Perform the actual installation"""
        steps = [
            ("Creating disk partitions...", "current"),
            ("Formatting partitions...", "pending"),
            ("Mounting partitions...", "pending"),
            ("Installing base system...", "pending"),
            ("Generating filesystem table...", "pending")
        ]
        
        try:
            # Partition disk
            self.tui.show_progress("Installing System", steps, step=6, total_steps=6)
            
            if self.config['uefi']:
                success = create_uefi_partitions(self.config['disk'])
            else:
                success = create_bios_partitions(self.config['disk'])
            
            if not success:
                raise Exception("Failed to create partitions")
            
            steps[0] = ("Disk partitions created", "completed")
            steps[1] = ("Formatting partitions...", "current")
            self.tui.show_progress("Installing System", steps, step=6, total_steps=6)
            
            # Format partitions
            if not format_partitions(self.config['disk'], self.config['uefi']):
                raise Exception("Failed to format partitions")
            
            steps[1] = ("Partitions formatted", "completed")
            steps[2] = ("Mounting partitions...", "current")
            self.tui.show_progress("Installing System", steps, step=6, total_steps=6)
            
            # Mount partitions
            if not mount_partitions(self.config['disk'], self.config['uefi']):
                raise Exception("Failed to mount partitions")
            
            steps[2] = ("Partitions mounted", "completed")
            steps[3] = ("Installing base system (this may take a while)...", "current")
            self.tui.show_progress("Installing System", steps, step=6, total_steps=6)
            
            # Install base system
            install_cmd = "pacstrap /mnt base linux linux-firmware networkmanager grub wpa_supplicant dialog vim"
            if not run_command(install_cmd, capture_output=False):
                raise Exception("Failed to install base system")
            
            steps[3] = ("Base system installed", "completed")
            steps[4] = ("Generating filesystem table...", "current")
            self.tui.show_progress("Installing System", steps, step=6, total_steps=6)
            
            # Generate fstab
            if not generate_fstab():
                raise Exception("Failed to generate fstab")
            
            steps[4] = ("Filesystem table created", "completed")
            self.tui.show_progress("Installing System", steps, step=6, total_steps=6)
            
            time.sleep(2)  # Let user see completion
            return True
            
        except Exception as e:
            error_steps = steps.copy()
            for i, (desc, status) in enumerate(error_steps):
                if status == "current":
                    error_steps[i] = (f"{desc} FAILED", "error")
                    break
            
            self.tui.show_progress("Installation Failed", error_steps, step=6, total_steps=6)
            self.tui.show_info_screen("Error", [f"ERROR: {str(e)}"], step=6, total_steps=6)
            return False
    
    def completion(self):
        """Show completion message"""
        lines = [
            "🎉 Installation Phase 1 Complete!",
            "",
            "📋 What has been installed:",
            "  ✓ Base Arch Linux system",
            "  ✓ Linux kernel and firmware", 
            "  ✓ Basic filesystem structure",
            "  ✓ Package manager (pacman)",
            "",
            "🔄 Next phases will include:",
            "  • System configuration (users, bootloader)",
            "  • Software installation (development tools)",
            "  • Hyprland desktop environment",
            "  • Personal dotfiles and customization",
            "",
            "The installation will continue automatically..."
        ]
        
        self.tui.show_info_screen("Installation Complete", lines, step=6, total_steps=6)
    
    def phase2_system_configuration(self):
        """Phase 2: System configuration with chroot"""
        steps = [
            ("Setting up timezone...", "current"),
            ("Configuring locales...", "pending"),
            ("Setting hostname and network...", "pending"),
            ("Creating users and passwords...", "pending"),
            ("Installing bootloader...", "pending")
        ]
        
        try:
            # Setup timezone
            self.tui.show_progress("System Configuration", steps, step=7, total_steps=8)
            
            if not setup_timezone(self.config['timezone']):
                raise Exception("Failed to setup timezone")
            
            steps[0] = ("Timezone configured", "completed")
            steps[1] = ("Configuring locales...", "current")
            self.tui.show_progress("System Configuration", steps, step=7, total_steps=8)
            
            # Setup locales
            if not setup_locales(self.config['locale']):
                raise Exception("Failed to setup locales")
            
            steps[1] = ("Locales configured", "completed")
            steps[2] = ("Setting hostname and network...", "current")
            self.tui.show_progress("System Configuration", steps, step=7, total_steps=8)
            
            # Setup hostname and network
            if not setup_hostname(self.config['hostname']):
                raise Exception("Failed to setup hostname")
            
            if not setup_network():
                raise Exception("Failed to setup network")
            
            steps[2] = ("Hostname and network configured", "completed")
            steps[3] = ("Creating users and passwords...", "current")
            self.tui.show_progress("System Configuration", steps, step=7, total_steps=8)
            
            # Setup users
            if not setup_users(self.config['username'], self.config['root_password'], self.config['user_password']):
                raise Exception("Failed to setup users")
            
            steps[3] = ("Users and passwords configured", "completed")
            steps[4] = ("Installing bootloader...", "current")
            self.tui.show_progress("System Configuration", steps, step=7, total_steps=8)
            
            # Setup bootloader
            if not setup_bootloader(self.config['uefi'], self.config['disk']):
                raise Exception("Failed to setup bootloader")
            
            steps[4] = ("Bootloader installed", "completed")
            self.tui.show_progress("System Configuration", steps, step=7, total_steps=8)
            
            time.sleep(2)
            return True
            
        except Exception as e:
            error_steps = steps.copy()
            for i, (desc, status) in enumerate(error_steps):
                if status == "current":
                    error_steps[i] = (f"{desc} FAILED", "error")
                    break
            
            self.tui.show_progress("Configuration Failed", error_steps, step=7, total_steps=8)
            self.tui.show_info_screen("Error", [f"ERROR: {str(e)}"], step=7, total_steps=8)
            return False
    
    def phase2_completion(self):
        """Show Phase 2 completion message"""
        lines = [
            "🎉 Phase 2 Configuration Complete!",
            "",
            "📋 System is now fully configured:",
            "  ✓ Timezone and locales set",
            "  ✓ Hostname and network configured", 
            "  ✓ Users and passwords created",
            "  ✓ GRUB bootloader installed",
            "  ✓ System ready to boot",
            "",
            "🔄 Next phases will include:",
            "  • Essential software installation",
            "  • Hyprland desktop environment",
            "  • Personal dotfiles and customization",
            "",
            "System installation completed successfully!"
        ]
        
        self.tui.show_info_screen("System Ready!", lines, step=8, total_steps=8)
    
    def run(self):
        """Run the installer"""
        try:
            self.tui.init_screen()
            
            if not self.welcome_screen():
                return
            
            if not self.system_checks():
                return
            
            if not self.select_disk():
                return
            
            if not self.basic_config():
                return
            
            if not self.installation_summary():
                return
            
            if not self.install_system():
                return
            
            self.completion()
            
            if not self.phase2_system_configuration():
                return
            
            self.phase2_completion()
            
        except KeyboardInterrupt:
            pass
        except Exception as e:
            error_msg = str(e)
            if "Terminal too small" in error_msg:
                print("\n" + "="*60)
                print("TERMINAL TOO SMALL")
                print("="*60)
                print(f"Error: {error_msg}")
                print("\nPlease resize your terminal window and try again.")
                print("Minimum required size: 60 columns x 20 rows")
                print("="*60)
            else:
                try:
                    self.tui.show_info_screen("Unexpected Error", [f"ERROR: {error_msg}"])
                except:
                    print(f"\nUnexpected error: {error_msg}")
        finally:
            self.tui.cleanup()


def main():
    installer = ArchInstaller()
    installer.run()


if __name__ == "__main__":
    main()
