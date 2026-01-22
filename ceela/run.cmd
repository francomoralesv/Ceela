@echo off

python3.12 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload