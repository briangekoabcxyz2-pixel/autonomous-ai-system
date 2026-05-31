#!/bin/bash
cd ~/autonomous-ai-system
source venv/bin/activate

echo "Starting AAES..."

nohup python3 autonomous_loop.py > logs/loop.log 2>&1 &
echo "Autonomous loop started"

nohup python3 dashboard/backend.py > logs/backend.log 2>&1 &
echo "Dashboard backend started"

cd dashboard/frontend && npm run dev &
echo "Dashboard frontend started"

echo "AAES running! Open http://localhost:5173"
