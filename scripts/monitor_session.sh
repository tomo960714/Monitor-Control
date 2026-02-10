#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-}"

case "$ACTION" in
  start)
    # Start the session monitor process here (e.g., using a command or script)
    /usr/bin/python3 -m monitor_control.cli on --display 1
    #/usr/bin/python3 -m monitor_control.cli on --display 2
    ;;
  stop)
    # Stop the session monitor process here (e.g., using a command or script)
    /usr/bin/python3 -m monitor_control.cli off --display 1
    /usr/bin/python3 -m monitor_control.cli off --display 2
    ;;
  *)
    echo "Usage: monitor_session.sh {start|stop}"
    exit 1
    ;;
esac