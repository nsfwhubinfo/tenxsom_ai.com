#!/usr/bin/env python3

"""
Tenxsom AI Flow Engine Worker (Deprecated)
This file is deprecated - video processing is now handled by cloud_tasks_worker.py
Jobs are processed via Google Cloud Tasks instead of Redis polling.

For production use:
- cloud_tasks_worker.py: Flask-based HTTP worker for Cloud Tasks
- run_flow.py: Job submission to Cloud Tasks queue

This file is kept for reference only.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def deprecated_worker_notice():
    """Display deprecation notice"""
    print("=" * 60)
    print("DEPRECATED: worker.py is no longer used in production")
    print("=" * 60)
    print("")
    print("The video generation system now uses Google Cloud Tasks.")
    print("")
    print("For production:")
    print("1. Use cloud_tasks_worker.py for job processing")
    print("2. Use run_flow.py for job submission")
    print("")
    print("Start the Cloud Tasks worker:")
    print("  python3 cloud_tasks_worker.py --host 0.0.0.0 --port 8080")
    print("")
    print("Submit jobs:")
    print("  python3 run_flow.py single --topic 'Your Topic'")
    print("")
    print("=" * 60)

if __name__ == "__main__":
    deprecated_worker_notice()