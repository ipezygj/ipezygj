#!/bin/bash
# Stealth Watchdog for V12 Engine
while true; do
    if ! pgrep -f "python -u .*strategy.py" > /dev/null; then
        echo "[$(date -Iseconds)] ⚠️ V12 Engine offline. Engaging auto-restart..." >> ~/my_ferrari/watchdog.log
        python -u ~/my_ferrari/strategy.py > ~/my_ferrari/strategy.log 2>&1 &
    fi
    sleep 600
done
