#!/bin/bash
# Fleet health check shortcut
cd "$(dirname "$0")/../.."
python3 tools/fleet/check-centurions.py
