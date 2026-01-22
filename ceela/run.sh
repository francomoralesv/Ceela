#!/bin/bash
#uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload --workers 4
source venv/bin/activate
gunicorn -w 2 --threads 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001 src.main:app --timeout 3600