#!/usr/bin/env python3
"""
SleepGuard UI Dashboard - Real-time monitoring interface
Displays live statistics from the SleepGuard daemon
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Try to import colorama for cross-platform colored output
try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback to no colors
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""

class SleepGuardUI:
    def __init__(self, stats_path="stats.json"):
        self.stats_path = stats_path
        self.last_update = None
        
    def clear_screen(self):
        """Clear terminal screen (cross-platform)"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_fatigue_color(self, score):
        """Get color based on fatigue score"""
        if score >= 90:
            return Fore.RED + Back.RED + Style.BRIGHT
        elif score >= 60:
            return Fore.RED + Style.BRIGHT
        elif score >= 30:
            return Fore.YELLOW + Style.BRIGHT
        else:
            return Fore.GREEN + Style.BRIGHT
    
    def get_mode_text(self, score):
        """Get mode text based on fatigue score"""
        if score >= 90:
            return "CRITICAL ⚠️"
        elif score >= 60:
            return "WARNING ⚡"
        elif score >= 30:
            return "CAUTION 💡"
        else:
            return "NORMAL ✓"
    
    def format_duration(self, seconds):
        """Format duration in HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def draw_progress_bar(self, value, max_value=100, length=30):
        """Draw a text-based progress bar"""
        filled = int((value / max_value) * length)
        bar = "█" * filled + "░" * (length - filled)
        return bar
    
    def load_stats(self):
        """Load statistics from JSON file"""
        try:
            if Path(self.stats_path).exists():
                with open(self.stats_path, 'r') as f:
                    return json.load(f)
            else:
                return None
        except Exception as e:
            return {"error": str(e)}
    
    def display_logo(self):
        """Display ASCII art logo"""
        logo = f"""
{Fore.CYAN}{Style.BRIGHT}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗██╗     ███████╗███████╗██████╗  ██████╗       ║
║   ██╔════╝██║     ██╔════╝██╔════╝██╔══██╗██╔════╝       ║
║   ███████╗██║     █████╗  █████╗  ██████╔╝██║  ███╗      ║
║   ╚════██║██║     ██╔══╝  ██╔══╝  ██╔═══╝ ██║   ██║      ║
║   ███████║███████╗███████╗███████╗██║     ╚██████╔╝      ║
║   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝       ║
║                                                           ║
║          Intelligent Productivity Protector               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        return logo
    
    def display_dashboard(self, stats):
        """Display the main dashboard"""
        self.clear_screen()
        
        # Display logo
        print(self.display_logo())
        
        if stats is None:
            print(f"{Fore.RED}⚠️  Daemon not running or stats file not found!")
            print(f"{Fore.YELLOW}Please start the daemon first: python sleepguard_daemon.py")
            return
        
        if "error" in stats:
            print(f"{Fore.RED}Error loading stats: {stats['error']}")
            return
        
        # Extract stats
        fatigue_score = stats.get('fatigue_score', 0)
        session_duration = stats.get('session_duration_seconds', 0)
        total_keystrokes = stats.get('total_keystrokes', 0)
        keystroke_rate = stats.get('current_keystroke_rate', 0)
        current_hour = stats.get('current_hour', datetime.now().hour)
        timestamp = stats.get('timestamp', '')
        
        # System info
        cpu_percent = stats.get('system_info', {}).get('cpu_percent', 0)
        memory_percent = stats.get('system_info', {}).get('memory_percent', 0)
        
        # Current time and mode
        current_time = datetime.now().strftime('%H:%M:%S')
        mode_text = self.get_mode_text(fatigue_score)
        mode_color = self.get_fatigue_color(fatigue_score)
        
        # Main stats display
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}Current Time: {Fore.YELLOW}{current_time}")
        print(f"{Fore.WHITE}Last Update:  {Fore.YELLOW}{timestamp.split('T')[1][:8] if timestamp else 'N/A'}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Mode status
        print(f"{Fore.WHITE}System Mode:  {mode_color}{mode_text:^20}{Style.RESET_ALL}\n")
        
        # Fatigue score with progress bar
        print(f"{Fore.WHITE}Fatigue Score:")
        fatigue_color = self.get_fatigue_color(fatigue_score)
        bar = self.draw_progress_bar(fatigue_score)
        print(f"  {fatigue_color}{bar} {fatigue_score}%{Style.RESET_ALL}\n")
        
        # Session info
        print(f"{Fore.CYAN}{'─'*60}")
        print(f"{Fore.WHITE}📊 Session Statistics:")
        print(f"{Fore.CYAN}{'─'*60}")
        print(f"{Fore.WHITE}  Duration:        {Fore.GREEN}{self.format_duration(session_duration)}")
        print(f"{Fore.WHITE}  Total Keystrokes: {Fore.GREEN}{total_keystrokes:,}")
        print(f"{Fore.WHITE}  Current Rate:     {Fore.GREEN}{keystroke_rate} keys/min")
        
        # Keystroke rate indicator
        rate_status = "Active 🔥" if keystroke_rate > 60 else "Slow 🐌" if keystroke_rate > 20 else "Idle 😴"
        rate_color = Fore.GREEN if keystroke_rate > 60 else Fore.YELLOW if keystroke_rate > 20 else Fore.RED
        print(f"{Fore.WHITE}  Activity:         {rate_color}{rate_status}\n")
        
        # System resources
        print(f"{Fore.CYAN}{'─'*60}")
        print(f"{Fore.WHITE}💻 System Resources:")
        print(f"{Fore.CYAN}{'─'*60}")
        print(f"{Fore.WHITE}  CPU Usage:    {self.draw_progress_bar(cpu_percent, length=20)} {cpu_percent:.1f}%")
        print(f"{Fore.WHITE}  Memory Usage: {self.draw_progress_bar(memory_percent, length=20)} {memory_percent:.1f}%\n")
        
        # Health recommendations
        print(f"{Fore.CYAN}{'─'*60}")
        print(f"{Fore.WHITE}💡 Health Recommendations:")
        print(f"{Fore.CYAN}{'─'*60}")
        
        if fatigue_score >= 90:
            print(f"{Fore.RED}  • STOP WORKING IMMEDIATELY!")
            print(f"{Fore.RED}  • You are in critical fatigue zone")
            print(f"{Fore.RED}  • Save your work and sleep NOW")
        elif fatigue_score >= 60:
            print(f"{Fore.YELLOW}  • Take a 15-minute break")
            print(f"{Fore.YELLOW}  • Get some water and stretch")
            print(f"{Fore.YELLOW}  • Consider wrapping up soon")
        elif fatigue_score >= 30:
            print(f"{Fore.YELLOW}  • Time for a short break")
            print(f"{Fore.YELLOW}  • Look away from screen (20-20-20 rule)")
        else:
            print(f"{Fore.GREEN}  • You're doing great! Keep it up")
            print(f"{Fore.GREEN}  • Remember to take regular breaks")
        
        # Time-based warnings
        if current_hour >= 23 or current_hour < 6:
            print(f"\n{Fore.RED}  ⚠️  It's late! Consider getting rest soon")
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}Press Ctrl+C to exit")
        print(f"{Fore.CYAN}{'='*60}")
    
    def run(self, refresh_interval=2):
        """Run the dashboard with auto-refresh"""
        print(f"{Fore.CYAN}Starting SleepGuard Dashboard...")
        print(f"{Fore.YELLOW}Refresh interval: {refresh_interval} seconds")
        time.sleep(1)
        
        try:
            while True:
                stats = self.load_stats()
                self.display_dashboard(stats)
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            self.clear_screen()
            print(f"\n{Fore.CYAN}SleepGuard Dashboard closed. Stay healthy! 💚")

if __name__ == "__main__":
    # Check if colorama is available
    if not COLORAMA_AVAILABLE:
        print("Note: Install 'colorama' for colored output: pip install colorama")
        time.sleep(2)
    
    ui = SleepGuardUI()
    ui.run(refresh_interval=2)