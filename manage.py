#!/usr/bin/env python
import os
import sys
import redis

def check_redis():
    try:
        r = redis.Redis(host='127.0.0.1', port=6379, db=1)
        r.ping() 
    except redis.ConnectionError:
        print("Error: Redis server is not running. Please start Redis.")
        sys.exit(1)

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nusarp.settings')
    check_redis()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()