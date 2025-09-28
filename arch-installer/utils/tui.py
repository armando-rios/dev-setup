#!/usr/bin/env python3
"""
Terminal User Interface using curses for archinstall-like experience
"""

import curses
import curses.textpad
import time
import textwrap


class TUI:
    def __init__(self):
        self.stdscr = None
        self.height = 0
        self.width = 0
        
    def init_screen(self):
        """Initialize curses screen"""
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.curs_set(0)  # Hide cursor
        
        # Initialize colors - black background with colored status indicators
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Header (white on black)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Selected item (black on white)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Success (green on black)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Error (red on black)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Warning (yellow on black)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Info (cyan on black)
        
        self.height, self.width = self.stdscr.getmaxyx()
        
        # Check minimum terminal size
        if self.height < 20 or self.width < 60:
            raise Exception(f"Terminal too small! Need at least 60x20, got {self.width}x{self.height}")
    
    def safe_addstr(self, y, x, text, attr=0):
        """Safely add string to screen with bounds checking"""
        try:
            if y >= 0 and y < self.height and x >= 0 and x < self.width:
                max_len = self.width - x - 1
                if len(text) > max_len:
                    text = text[:max_len]
                self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass
        
    def cleanup(self):
        """Cleanup curses"""
        if self.stdscr:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()
    
    def draw_header(self, title, step=None, total_steps=None):
        """Draw header bar"""
        self.stdscr.clear()
        
        # Header background
        header_text = f" Arch Linux Installer - {title} "
        if step and total_steps:
            header_text += f"[{step}/{total_steps}]"
        
        self.safe_addstr(0, 0, header_text, curses.A_BOLD)
        
        # Draw separator
        self.safe_addstr(1, 0, "─" * self.width)
        
    def draw_footer(self, instructions="Use ↑↓/jk arrows, Enter to select, q to quit"):
        """Draw footer with instructions"""
        footer_y = self.height - 1
        self.safe_addstr(footer_y, 2, instructions)
        
    def show_menu(self, title, options, selected=0, step=None, total_steps=None):
        """Show interactive menu with keyboard navigation"""
        while True:
            self.draw_header(title, step, total_steps)
            
            # Menu content area
            start_y = 3
            max_visible = self.height - 6  # Reserve space for header and footer
            
            # Calculate visible range
            if len(options) > max_visible:
                if selected < max_visible // 2:
                    start_idx = 0
                elif selected > len(options) - max_visible // 2:
                    start_idx = len(options) - max_visible
                else:
                    start_idx = selected - max_visible // 2
                end_idx = min(start_idx + max_visible, len(options))
            else:
                start_idx = 0
                end_idx = len(options)
            
            # Draw options
            for i, option in enumerate(options[start_idx:end_idx], start_idx):
                y = start_y + i - start_idx
                
                if i == selected:
                    # Highlight selected option
                    self.safe_addstr(y, 2, f"> {option}", curses.color_pair(2) | curses.A_BOLD)
                else:
                    self.safe_addstr(y, 2, f"  {option}")
            
            # Show scrolling indicator if needed
            if len(options) > max_visible:
                if start_idx > 0:
                    self.safe_addstr(start_y - 1, self.width - 3, "↑")
                if end_idx < len(options):
                    self.safe_addstr(start_y + max_visible, self.width - 3, "↓")
            
            self.draw_footer()
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            # Navigation: both arrow keys and vim-like keys
            if (key == curses.KEY_UP or key == ord('k')) and selected > 0:
                selected -= 1
            elif (key == curses.KEY_DOWN or key == ord('j')) and selected < len(options) - 1:
                selected += 1
            elif key == ord('\n') or key == ord(' '):
                return selected
            elif key == ord('q') or key == 27:  # ESC
                return -1
    
    def show_text_input(self, title, prompt, default="", step=None, total_steps=None):
        """Show text input dialog"""
        curses.curs_set(1)  # Show cursor
        
        while True:
            self.draw_header(title, step, total_steps)
            
            # Draw prompt
            start_y = 4
            self.safe_addstr(start_y, 2, prompt)
            
            if default:
                self.safe_addstr(start_y + 2, 2, f"Default: {default}")
                self.safe_addstr(start_y + 3, 2, "Press Enter for default, or type new value:")
            
            # Input field
            input_y = start_y + 4
            self.safe_addstr(input_y, 2, "> ")
            
            # Create input window
            input_win = curses.newwin(1, self.width - 6, input_y, 4)
            textbox = curses.textpad.Textbox(input_win)
            
            self.draw_footer("Enter text, Ctrl+G to finish")
            self.stdscr.refresh()
            
            # Get input
            result = textbox.edit().strip()
            
            if not result and default:
                result = default
            
            curses.curs_set(0)  # Hide cursor
            
            if result or not default:
                return result
    
    def show_password_input(self, title, prompt, step=None, total_steps=None):
        """Show password input dialog with hidden characters"""
        import getpass
        
        self.draw_header(title, step, total_steps)
        
        # Draw prompt
        start_y = 4
        self.safe_addstr(start_y, 2, prompt)
        self.safe_addstr(start_y + 2, 2, "Password will be hidden as you type")
        self.safe_addstr(start_y + 4, 2, "> ")
        
        self.draw_footer("Type password, Enter to finish")
        self.stdscr.refresh()
        
        # Temporarily exit curses to use getpass
        curses.endwin()
        
        try:
            password = getpass.getpass("")
            return password
        finally:
            # Reinitialize curses
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            curses.curs_set(0)
    
    def show_confirmation(self, title, message, default=True, step=None, total_steps=None):
        """Show yes/no confirmation dialog"""
        options = ["Yes", "No"]
        selected = 0 if default else 1
        
        while True:
            self.draw_header(title, step, total_steps)
            
            # Draw message
            start_y = 4
            lines = textwrap.wrap(message, self.width - 4)
            for i, line in enumerate(lines):
                self.safe_addstr(start_y + i, 2, line)
            
            # Draw options
            option_y = start_y + len(lines) + 2
            for i, option in enumerate(options):
                x = 10 + i * 15
                if i == selected:
                    self.safe_addstr(option_y, x, f"[{option}]", curses.color_pair(2) | curses.A_BOLD)
                else:
                    self.safe_addstr(option_y, x, f" {option} ")
            
            self.draw_footer("Use ←→/hl arrows, Enter to select")
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            # Navigation: both arrow keys and vim-like keys
            if (key == curses.KEY_LEFT or key == ord('h')) and selected > 0:
                selected -= 1
            elif (key == curses.KEY_RIGHT or key == ord('l')) and selected < len(options) - 1:
                selected += 1
            elif key == ord('\n'):
                return selected == 0
            elif key == ord('q') or key == 27:  # ESC
                return False
    
    def show_progress(self, title, steps, step=None, total_steps=None):
        """Show progress screen with steps"""
        self.draw_header(title, step, total_steps)
        
        start_y = 4
        for i, (step_desc, status) in enumerate(steps):
            y = start_y + i
            
            if status == "completed":
                self.safe_addstr(y, 2, "✓ ", curses.color_pair(3))
            elif status == "current":
                self.safe_addstr(y, 2, "▶ ", curses.color_pair(6))
            elif status == "error":
                self.safe_addstr(y, 2, "✗ ", curses.color_pair(4))
            else:
                self.safe_addstr(y, 2, "  ")
            
            self.safe_addstr(y, 4, step_desc)
        
        self.stdscr.refresh()
    
    def show_info_screen(self, title, lines, step=None, total_steps=None, wait_for_key=True):
        """Show information screen"""
        self.draw_header(title, step, total_steps)
        
        start_y = 4
        for i, line in enumerate(lines):
            if i + start_y >= self.height - 2:
                break
            
            # Handle colored lines with status colors
            if line.startswith("SUCCESS: "):
                self.safe_addstr(start_y + i, 2, line[9:], curses.color_pair(3))
            elif line.startswith("ERROR: "):
                self.safe_addstr(start_y + i, 2, line[7:], curses.color_pair(4))
            elif line.startswith("WARNING: "):
                self.safe_addstr(start_y + i, 2, line[9:], curses.color_pair(5))
            elif line.startswith("INFO: "):
                self.safe_addstr(start_y + i, 2, line[6:], curses.color_pair(6))
            else:
                self.safe_addstr(start_y + i, 2, line)
        
        if wait_for_key:
            self.draw_footer("Press any key to continue...")
            self.stdscr.refresh()
            self.stdscr.getch()
        else:
            self.stdscr.refresh()
    
    def show_summary(self, title, config, step=None, total_steps=None):
        """Show configuration summary"""
        lines = [
            "Installation Configuration:",
            "",
            f"System Type:     {'UEFI' if config.get('uefi') else 'BIOS'}",
            f"Target Disk:     {config.get('disk', 'Not selected')}",
            f"Hostname:        {config.get('hostname', 'arch')}",
            f"Username:        {config.get('username', 'user')}",
            f"Timezone:        {config.get('timezone', 'UTC')}",
            f"Locale:          {config.get('locale', 'en_US.UTF-8')}",
            f"Root Password:   {'Set' if config.get('root_password') else 'Not set'}",
            f"User Password:   {'Set' if config.get('user_password') else 'Not set'}",
            "",
            "WARNING: This will PERMANENTLY ERASE the selected disk!"
        ]
        
        self.show_info_screen(title, lines, step, total_steps, wait_for_key=False)
        return self.show_confirmation("Confirm Installation", 
                                    "Proceed with installation?", 
                                    default=False)