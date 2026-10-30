#!/usr/bin/env bash
# One-off (Cloud Claude msg #26): let the running embed.py NEW finish gte-base, stop it before it
# moves on (its next model would be nomic/arctic, then mxbai), then continue with resume_all.sh.
cd "$(dirname "$0")"
P=33299
while kill -0 $P 2>/dev/null && ! grep -q "^NEW gte-base {" results_log_NEW.txt; do sleep 5; done
sleep 3   # let embed.py finish writing _env.json after the print
kill $P 2>/dev/null && echo "stopped embed.py NEW after gte-base at $(date '+%F %T')"
sleep 5
exec bash resume_all.sh
