#!/bin/bash
kill $(lsof -ti:5001) 2>/dev/null
sleep 1
python3 app.py > /tmp/flask.log 2>&1 &
echo "Server started with PID $!"
sleep 3
echo "Server running at http://localhost:5001"
