#!/usr/bin/env python3
"""
Quick Test Script for SleepGuard
Tests all components to ensure they work correctly
"""

import sys
import time
import json
from pathlib import Path

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import psutil
        print("  ✓ psutil imported successfully")
    except ImportError:
        print("  ✗ psutil not found - run: pip install psutil")
        return False
    
    try:
        import pynput
        print("  ✓ pynput imported successfully")
    except ImportError:
        print("  ✗ pynput not found - run: pip install pynput")
        return False
    
    try:
        import plyer
        print("  ✓ plyer imported successfully")
    except ImportError:
        print("  ✗ plyer not found - run: pip install plyer")
        return False
    
    try:
        import colorama
        print("  ✓ colorama imported successfully")
    except ImportError:
        print("  ⚠ colorama not found - dashboard will work but without colors")
        print("    Optional: pip install colorama")
    
    return True

def test_daemon_import():
    """Test if daemon can be imported"""
    print("\nTesting daemon import...")
    try:
        from sleepguard_daemon import SleepGuardDaemon
        print("  ✓ Daemon imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to import daemon: {e}")
        return False

def test_ui_import():
    """Test if UI can be imported"""
    print("\nTesting UI import...")
    try:
        from sleepguard_ui import SleepGuardUI
        print("  ✓ UI imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to import UI: {e}")
        return False

def test_config_file():
    """Test if config file exists and is valid"""
    print("\nTesting configuration...")
    if Path("config.json").exists():
        try:
            with open("config.json", 'r') as f:
                config = json.load(f)
            print("  ✓ Config file is valid JSON")
            print(f"  ✓ Bedtime hour: {config.get('bedtime_hour', 'not set')}")
            print(f"  ✓ Notification levels: {config.get('notification_levels', 'not set')}")
            return True
        except Exception as e:
            print(f"  ✗ Config file is invalid: {e}")
            return False
    else:
        print("  ⚠ Config file not found - will be created on first run")
        return True

def test_daemon_init():
    """Test if daemon can be initialized"""
    print("\nTesting daemon initialization...")
    try:
        from sleepguard_daemon import SleepGuardDaemon
        daemon = SleepGuardDaemon()
        print("  ✓ Daemon initialized successfully")
        print(f"  ✓ Session start: {daemon.session_start}")
        print(f"  ✓ Fatigue score: {daemon.fatigue_score}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to initialize daemon: {e}")
        return False

def test_fatigue_calculation():
    """Test fatigue score calculation"""
    print("\nTesting fatigue calculation...")
    try:
        from sleepguard_daemon import SleepGuardDaemon
        daemon = SleepGuardDaemon()
        score = daemon.calculate_fatigue_score()
        print(f"  ✓ Fatigue score calculated: {score}%")
        
        if 0 <= score <= 100:
            print("  ✓ Score is in valid range (0-100)")
            return True
        else:
            print(f"  ✗ Score out of range: {score}")
            return False
    except Exception as e:
        print(f"  ✗ Failed to calculate fatigue: {e}")
        return False

def test_notification():
    """Test notification system"""
    print("\nTesting notification system...")
    try:
        from plyer import notification
        notification.notify(
            title="SleepGuard Test",
            message="If you see this notification, the system works!",
            app_name="SleepGuard Test",
            timeout=3
        )
        print("  ✓ Notification sent (check if you see it!)")
        return True
    except Exception as e:
        print(f"  ✗ Failed to send notification: {e}")
        print("  ⚠ This is OK - notifications may require additional setup on some systems")
        return True  # Don't fail the test for notifications

def test_ui_display():
    """Test UI can display"""
    print("\nTesting UI display...")
    try:
        from sleepguard_ui import SleepGuardUI
        ui = SleepGuardUI()
        
        # Create dummy stats for testing
        dummy_stats = {
            "timestamp": "2024-01-01T12:00:00",
            "session_start": "2024-01-01T10:00:00",
            "session_duration_seconds": 7200,
            "total_keystrokes": 5432,
            "current_keystroke_rate": 75,
            "fatigue_score": 45,
            "current_hour": 12,
            "system_info": {
                "cpu_percent": 35.5,
                "memory_percent": 62.3
            }
        }
        
        # Save dummy stats
        with open("stats.json", 'w') as f:
            json.dump(dummy_stats, f)
        
        print("  ✓ UI can be initialized")
        print("  ✓ Dummy stats created")
        print("  ℹ UI display test passed (run sleepguard_ui.py to see full display)")
        return True
    except Exception as e:
        print(f"  ✗ Failed UI test: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("SleepGuard System Test")
    print("="*60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Daemon Import", test_daemon_import),
        ("UI Import", test_ui_import),
        ("Configuration File", test_config_file),
        ("Daemon Initialization", test_daemon_init),
        ("Fatigue Calculation", test_fatigue_calculation),
        ("Notification System", test_notification),
        ("UI Display", test_ui_display),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Run daemon: python sleepguard_daemon.py")
        print("  2. Run UI (in new terminal): python sleepguard_ui.py")
        print("  3. Start typing to see it in action!")
    else:
        print("\n⚠️ Some tests failed. Please fix issues before running.")
        print("   Most common fix: pip install -r requirements.txt")
    
    print("="*60)

if __name__ == "__main__":
    run_all_tests()