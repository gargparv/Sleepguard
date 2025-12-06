# SleepGuard - Intelligent Late-Night Productivity Protector

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An OS-level daemon that monitors your work patterns and intervenes when you're working unhealthy late hours. Protects developers and students from burnout by detecting fatigue and enforcing healthy work boundaries.

## 🎯 Features

- **Real-time Activity Monitoring**: Tracks keyboard activity, work duration, and system time
- **Intelligent Fatigue Detection**: Calculates fatigue score based on:
  - Time of day (higher penalties after bedtime)
  - Continuous work session duration
  - Keystroke rate and typing patterns
- **Progressive Interventions**: 
  - Desktop notifications at 30%, 60%, and 90% fatigue levels
  - Escalating warnings as fatigue increases
- **Live Dashboard**: Beautiful terminal UI showing real-time statistics
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Configurable**: Customize bedtime, notification levels, and more

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## 🚀 Installation

### 1. Clone or download this project

```bash
git clone <repository-url>
cd sleepguard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install psutil pynput plyer colorama
```

### 3. Verify installation

```bash
python sleepguard_daemon.py --help
```

## 💻 Usage

### Running the Daemon

The daemon runs in the background and monitors your activity:

```bash
python sleepguard_daemon.py
```

You should see:
```
[HH:MM:SS] SleepGuard Daemon initialized
Session started at: HH:MM:SS
[HH:MM:SS] Starting SleepGuard Daemon...
Press Ctrl+C to stop
```

The daemon will:
- Monitor all keyboard activity
- Calculate fatigue score every 5 seconds
- Send notifications when fatigue thresholds are reached
- Save statistics to `stats.json` every minute

### Running the Dashboard

In a separate terminal window, start the UI dashboard:

```bash
python sleepguard_ui.py
```

The dashboard displays:
- Current fatigue score with visual progress bar
- Session duration (HH:MM:SS)
- Total keystroke count
- Current keystroke rate (keys/min)
- System mode (NORMAL/CAUTION/WARNING/CRITICAL)
- CPU and memory usage
- Health recommendations

**Dashboard refreshes every 2 seconds automatically.**

### Stopping the System

Press `Ctrl+C` in either terminal to stop the daemon or dashboard.

## ⚙️ Configuration

Edit `config.json` to customize behavior:

```json
{
    "bedtime_hour": 23,              // 11 PM - when fatigue scoring increases
    "critical_hour": 2,              // 2 AM - critical fatigue zone
    "max_session_hours": 4,          // Maximum recommended work session
    "notification_levels": [30, 60, 90],  // Fatigue % for notifications
    "keystroke_window_seconds": 60,  // Time window for rate calculation
    "save_interval_seconds": 60      // Stats save frequency
}
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `bedtime_hour` | Hour after which fatigue increases (0-23) | 23 (11 PM) |
| `critical_hour` | Hour when critical mode activates | 2 (2 AM) |
| `max_session_hours` | Maximum continuous work hours | 4 hours |
| `notification_levels` | Fatigue thresholds for alerts | [30, 60, 90] |
| `keystroke_window_seconds` | Keystroke rate calculation window | 60 seconds |
| `save_interval_seconds` | How often stats are saved | 60 seconds |

## 📊 Understanding Fatigue Score

The fatigue score (0-100) is calculated from three factors:

### 1. Time of Day (30 points max)
- Increases significantly after `bedtime_hour`
- Penalty grows with each hour past bedtime
- Maximum penalty during `critical_hour` and beyond

### 2. Session Duration (40 points max)
- Starts adding points after 1 hour of continuous work
- Reaches maximum at `max_session_hours`
- Encourages taking breaks

### 3. Keystroke Rate (30 points max)
- Monitors typing activity in the last 60 seconds
- Lower activity = higher fatigue (you're slowing down)
- Scoring:
  - < 30 keys/min: 30 points (very low activity)
  - 30-60 keys/min: 20 points (below normal)
  - 60-90 keys/min: 10 points (normal)
  - \> 90 keys/min: 0 points (highly active)

### Fatigue Levels

- **0-29%**: NORMAL ✓ (Green) - You're doing great!
- **30-59%**: CAUTION 💡 (Yellow) - Consider a break soon
- **60-89%**: WARNING ⚡ (Orange/Red) - Take a break now
- **90-100%**: CRITICAL ⚠️ (Red) - STOP WORKING IMMEDIATELY

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     SleepGuard Daemon (Root)        │
│  (Runs continuously in background)  │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
   ┌───▼────┐     ┌───▼────┐
   │Monitor │     │ Policy │
   │ Engine │     │ Engine │
   └───┬────┘     └───┬────┘
       │              │
       │    ┌─────────▼──────────┐
       │    │ Fatigue Calculator │
       └───►│ - Time scoring     │
            │ - Duration scoring │
            │ - Keystroke scoring│
            └─────────┬──────────┘
                      │
            ┌─────────▼──────────┐
            │  Action Controller │
            │ - Notifications    │
            │ - Stats Logging    │
            └─────────┬──────────┘
                      │
                      ▼
                 stats.json
                      │
                      │
            ┌─────────▼──────────┐
            │   UI Dashboard     │
            │ (Real-time display)│
            └────────────────────┘
```

### Components

1. **Daemon (`sleepguard_daemon.py`)**
   - Background service
   - Monitors keyboard input via `pynput`
   - Calculates fatigue score
   - Sends notifications via `plyer`
   - Saves statistics to JSON

2. **Dashboard (`sleepguard_ui.py`)**
   - Terminal-based UI with `colorama`
   - Reads stats from JSON file
   - Auto-refreshes every 2 seconds
   - Displays health recommendations

3. **Configuration (`config.json`)**
   - User-customizable settings
   - Loaded at daemon startup

4. **Statistics (`stats.json`)**
   - Real-time data storage
   - Updated every 60 seconds
   - Read by dashboard for display

## 🔬 OS Concepts Demonstrated

### 1. Process Management & Monitoring
- Uses `psutil` to access system process information
- Monitors CPU and memory usage
- Demonstrates understanding of `/proc` filesystem (Linux) or equivalent

### 2. System Calls & Input Monitoring
- Hooks into low-level keyboard events via `pynput`
- Event-driven architecture
- Asynchronous input handling

### 3. Daemon/Service Architecture
- Runs as background process
- Continuous monitoring loop
- Signal handling (Ctrl+C for graceful shutdown)

### 4. Inter-Process Communication (IPC)
- File-based communication between daemon and UI
- JSON for structured data exchange
- Demonstrates shared data access patterns

### 5. Resource Control & Scheduling
- Time-based task scheduling (periodic saves)
- Multi-threading (keyboard listener + monitoring loop)
- Thread synchronization with locks

### 6. Notification System Integration
- OS-level desktop notifications
- Cross-platform notification API usage

## 📁 File Structure

```
sleepguard/
├── sleepguard_daemon.py    # Main daemon (background monitor)
├── sleepguard_ui.py        # Terminal dashboard
├── config.json             # Configuration file
├── stats.json              # Real-time statistics (auto-generated)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🐛 Troubleshooting

### Daemon won't start
- **Issue**: Permission errors on Linux/Mac
- **Solution**: Some input monitoring features may require elevated privileges:
  ```bash
  sudo python sleepguard_daemon.py
  ```

### Notifications not appearing
- **Issue**: `plyer` notification backend not configured
- **Solution**: Install platform-specific notification tools:
  - **Linux**: `sudo apt-get install libnotify-bin`
  - **macOS**: Notifications work out of the box
  - **Windows**: Notifications work out of the box

### Dashboard shows "Daemon not running"
- **Issue**: `stats.json` file not found
- **Solution**: Make sure the daemon is running first. It creates `stats.json` on first save.

### Colors not showing in dashboard
- **Issue**: `colorama` not installed or terminal doesn't support colors
- **Solution**: 
  ```bash
  pip install colorama
  ```

## 🎓 Educational Value

This project demonstrates:
- **Operating Systems**: Process management, system calls, daemons
- **Systems Programming**: Low-level I/O, event handling, threading
- **Software Engineering**: Modular design, configuration management
- **User Experience**: Progressive intervention, health-focused design
- **Real-world Application**: Addresses actual developer/student wellness

## 🚀 Future Enhancements

Potential improvements for further development:

1. **Machine Learning Integration**
   - Learn individual fatigue patterns
   - Personalized thresholds
   - Predictive alerts

2. **Application Blocking**
   - Force-close distracting apps
   - Whitelist essential applications
   - Kernel-level blocking

3. **Smart Home Integration**
   - Dim smart lights at high fatigue
   - Adjust room temperature
   - Play calming music

4. **Mobile Companion App**
   - Remote monitoring
   - Cross-device sync
   - Weekly health reports

5. **Advanced Analytics**
   - Weekly/monthly productivity reports
   - Optimal work time identification
   - Correlation with code quality metrics

## 📝 License

MIT License - Feel free to use and modify for educational purposes.

## 👨‍💻 Author

Parv Garg

## 🙏 Acknowledgments

- `psutil` - Cross-platform process utilities
- `pynput` - Keyboard and mouse input monitoring
- `plyer` - Platform-independent notification system
- `colorama` - Cross-platform colored terminal output

---

**Remember**: This tool is designed to help you maintain healthy work habits. Listen to your body, and don't override warnings too often! 💚
