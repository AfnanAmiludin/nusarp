#!/usr/bin/env python
import os
import sys
import time
import redis
import threading
from django.core.management import execute_from_command_line

running = True

def check_redis():
    """Check if Redis server is running."""
    try:
        r = redis.Redis(host='127.0.0.1', port=6379, db=1)
        r.ping()
        return True
    except redis.ConnectionError:
        return False

def monitor_redis():
    """Continuously check Redis status while Django server is running."""
    global running
    while running:
        if not check_redis():
            print("❌ Redis server stopped. Shutting down Django...")
            running = False
            os._exit(1) 
        time.sleep(3) 

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
    
    if not check_redis():
        print("❌ Error: Redis server is not running. Please start Redis first.")
        sys.exit(1)
    
    print("✅ Redis is running. Starting Django server...")
    
    # Start Redis monitoring
    thread = threading.Thread(target=monitor_redis, daemon=True)
    thread.start()

    try:
        execute_from_command_line(sys.argv)
    except KeyboardInterrupt:
        print("🛑 Stopping Django server...")
        running = False
        sys.exit(0)

if __name__ == '__main__':
    while True:
        try:
            main()
            break
        except SystemExit:
            print("Retrying in 5 seconds...")
            time.sleep(5)
