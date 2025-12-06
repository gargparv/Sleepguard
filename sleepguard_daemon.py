#!/usr/bin/env python3
"""
SleepGuard Daemon - Intelligent Late-Night Productivity Protector
Monitors user activity and intervenes when working unhealthy late hours
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import psutil
from pynput import keyboard
from plyer import notification

class SleepGuardDaemon:
    def __init__(self, config_path="config.json", stats_path="stats.json"):
        """Initialize the SleepGuard daemon"""
        self.config_path = config_path
        self.stats_path = stats_path
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize tracking variables
        self.session_start = datetime.now()
        self.keystroke_count = 0
        self.last_keystroke_time = datetime.now()
        self.keystroke_history = []  # Store timestamps of keystrokes
        self.fatigue_score = 0
        self.last_notification_level = 0
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        # Running flag
        self.running = True
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SleepGuard Daemon initialized")
        print(f"Session started at: {self.session_start.strftime('%H:%M:%S')}")
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Default configuration
                default_config = {
                    "bedtime_hour": 23,  # 11 PM
                    "critical_hour": 2,  # 2 AM
                    "max_session_hours": 4,
                    "notification_levels": [30, 60, 90],
                    "keystroke_window_seconds": 60,
                    "save_interval_seconds": 60
                }
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                print(f"Created default config at {self.config_path}")
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def on_press(self, key):
        """Callback for keyboard press events"""
        with self.lock:
            self.keystroke_count += 1
            current_time = datetime.now()
            self.last_keystroke_time = current_time
            self.keystroke_history.append(current_time)
            
            # Keep only recent keystrokes (last minute)
            cutoff_time = current_time - timedelta(
                seconds=self.config.get('keystroke_window_seconds', 60)
            )
            self.keystroke_history = [
                t for t in self.keystroke_history if t > cutoff_time
            ]
    
    def calculate_fatigue_score(self):
        """
        Calculate fatigue score (0-100) based on multiple factors:
        1. Time of day (30 points max)
        2. Session duration (40 points max)
        3. Keystroke rate decline (30 points max)
        """
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Factor 1: Time of day scoring
        time_score = 0
        bedtime = self.config.get('bedtime_hour', 23)
        critical_hour = self.config.get('critical_hour', 2)
        
        if current_hour >= bedtime or current_hour < 6:
            # Late night hours
            if current_hour >= bedtime:
                hours_past_bedtime = current_hour - bedtime
            else:
                # After midnight
                hours_past_bedtime = (24 - bedtime) + current_hour
            
            time_score = min(30, hours_past_bedtime * 7)
        
        # Factor 2: Session duration scoring
        session_duration = (current_time - self.session_start).total_seconds() / 3600
        max_session = self.config.get('max_session_hours', 4)
        
        if session_duration > 1:
            duration_score = min(40, (session_duration / max_session) * 40)
        else:
            duration_score = 0
        
        # Factor 3: Keystroke rate scoring
        keystroke_rate_score = 0
        if len(self.keystroke_history) > 0:
            # Calculate current keystroke rate (keystrokes per minute)
            current_rate = len(self.keystroke_history)
            
            # Expected normal rate: 60-120 keystrokes per minute when active
            # Lower rate indicates fatigue
            if current_rate < 30:
                # Very low activity
                keystroke_rate_score = 30
            elif current_rate < 60:
                # Below normal
                keystroke_rate_score = 20
            elif current_rate < 90:
                # Normal range
                keystroke_rate_score = 10
            else:
                # High activity (good)
                keystroke_rate_score = 0
        else:
            # No recent activity
            keystroke_rate_score = 25
        
        # Combine all scores
        total_score = time_score + duration_score + keystroke_rate_score
        return min(100, int(total_score))
    
    def send_notification(self, fatigue_level):
        """Send desktop notification based on fatigue level"""
        try:
            if fatigue_level >= 90:
                title = "🚨 SleepGuard: CRITICAL ALERT!"
                message = "You've been working way too long! Please rest NOW."
                timeout = 10
            elif fatigue_level >= 60:
                title = "⚠️ SleepGuard: High Fatigue Detected"
                message = "Consider taking a break soon. Your productivity is declining."
                timeout = 8
            elif fatigue_level >= 30:
                title = "💡 SleepGuard: Fatigue Warning"
                message = f"You've been working for {self.get_session_duration()}. Time for a break?"
                timeout = 5
            else:
                return
            
            notification.notify(
                title=title,
                message=message,
                app_name="SleepGuard",
                timeout=timeout
            )
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Notification sent: {title}")
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def get_session_duration(self):
        """Get formatted session duration"""
        duration = datetime.now() - self.session_start
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    def get_keystroke_rate(self):
        """Get current keystroke rate per minute"""
        if len(self.keystroke_history) > 0:
            return len(self.keystroke_history)
        return 0
    
    def save_stats(self):
        """Save current statistics to JSON file"""
        try:
            with self.lock:
                stats = {
                    "timestamp": datetime.now().isoformat(),
                    "session_start": self.session_start.isoformat(),
                    "session_duration_seconds": (datetime.now() - self.session_start).total_seconds(),
                    "total_keystrokes": self.keystroke_count,
                    "current_keystroke_rate": self.get_keystroke_rate(),
                    "fatigue_score": self.fatigue_score,
                    "current_hour": datetime.now().hour,
                    "system_info": {
                        "cpu_percent": psutil.cpu_percent(interval=0.1),
                        "memory_percent": psutil.virtual_memory().percent
                    }
                }
            
            with open(self.stats_path, 'w') as f:
                json.dump(stats, f, indent=4)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Stats saved - "
                  f"Fatigue: {self.fatigue_score}%, "
                  f"Keystrokes: {self.keystroke_count}, "
                  f"Rate: {self.get_keystroke_rate()}/min")
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        last_save_time = datetime.now()
        save_interval = self.config.get('save_interval_seconds', 60)
        
        while self.running:
            try:
                # Calculate current fatigue score
                with self.lock:
                    self.fatigue_score = self.calculate_fatigue_score()
                    current_score = self.fatigue_score
                
                # Check if we need to send notifications
                notification_levels = self.config.get('notification_levels', [30, 60, 90])
                for level in sorted(notification_levels):
                    if current_score >= level and self.last_notification_level < level:
                        self.send_notification(current_score)
                        self.last_notification_level = level
                        break
                
                # Reset notification level if fatigue decreases
                if current_score < 30:
                    self.last_notification_level = 0
                
                # Save stats periodically
                if (datetime.now() - last_save_time).total_seconds() >= save_interval:
                    self.save_stats()
                    last_save_time = datetime.now()
                
                # Sleep for a short interval
                time.sleep(5)
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(5)
    
    def start(self):
        """Start the daemon"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting SleepGuard Daemon...")
        print("Press Ctrl+C to stop")
        
        # Start keyboard listener in a separate thread
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
        
        # Start monitoring loop
        try:
            self.monitor_loop()
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Stopping SleepGuard Daemon...")
            self.running = False
            listener.stop()
            self.save_stats()  # Final save
            print("Daemon stopped successfully")

if __name__ == "__main__":
    daemon = SleepGuardDaemon()
    daemon.start()