#!/bin/bash
# REM ERP watchdog: ensure Redis + bench are running (MariaDB auto-starts in WSL).
# Runs every 5 min via Windows Task Scheduler "REM ERP Watchdog".
# FIX (2026-08-09): the previous `setsid nohup bench start &` died with the
# task-spawned shell, so every tick saw "bench down", killed the healthy
# tool-started bench, and started another doomed one. Now uses
# `setsid ... </dev/null >/dev/null 2>&1 &` (fully detached, survives parent
# exit) and only kills port holders when the port is genuinely empty.
export PATH="$HOME/.local/bin:$PATH"
LOG=/tmp/rem-watchdog.log

# 1. Redis (no systemd → must start manually after reboot)
redis-cli -p 11000 ping >/dev/null 2>&1 || { echo "$(date '+%F %T') redis 11000 down — starting" >> "$LOG"; redis-server --port 11000 --daemonize yes; }
redis-cli -p 13000 ping >/dev/null 2>&1 || { echo "$(date '+%F %T') redis 13000 down — starting" >> "$LOG"; redis-server --port 13000 --daemonize yes; }

# 2. Bench web (port 8000) — check the LISTENER, not curl (curl can false-fail
#    during bench startup while a listener already exists; and a healthy bench
#    was being killed on every tick)
if ! ss -tlnp 2>/dev/null | grep -q ":8000 "; then
  echo "$(date '+%F %T') bench down (no :8000 listener) — starting" >> "$LOG"
  cd ~/frappe-bench
  # clear any stale socketio on 9000 first (the EADDRINUSE killer)
  for port in 8000 9000; do
    PIDS=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -oE "pid=[0-9]+" | cut -d= -f2 | sort -u)
    for pid in $PIDS; do kill -9 "$pid" 2>/dev/null; done
  done
  pkill -9 -f honcho 2>/dev/null
  pkill -9 -f bench_helper 2>/dev/null
  pkill -9 -f "realtime/index.js" 2>/dev/null
  pkill -9 -f esbuild 2>/dev/null
  sleep 3
  # fully detached: setsid + all fds redirected; survives the task shell exit
  setsid nohup bench start </dev/null >/tmp/bench-start.log 2>&1 &
  disown
  # a later tick re-checks; give it ~40s head start
fi
exit 0
