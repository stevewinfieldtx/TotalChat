# README.md.txt
# Placeholder file for AI Influencer Platform
# This file will contain the actual implementation
# TotalChat Developer Guide

File: README.md.txt
Location: .
Status: Placeholder - implementation needed
This repository contains a FastAPI websocket backend and a React/Vite frontend for
running multi-character conversations. The previous placeholder README has been
replaced with concrete steps so you can boot the stack and try a "basic chat"
round-trip locally.

## Prerequisites
- Python 3.10+
- Node.js 18+
- `pip` and `npm`

## 1. Install backend dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\\Scripts\\activate`
pip install fastapi uvicorn websockets
```

## 2. Start the websocket backend
```bash
uvicorn backend.server:app --reload --port 8000
```
This exposes the websocket endpoint at `ws://127.0.0.1:8000/ws/<client_id>`.

## 3. (Optional) Start the React frontend
The shipped frontend is still evolving, but you can boot the development server
for layout checks.
```bash
cd frontend
npm install
npm run dev
```
Vite prints the local URL (usually `http://127.0.0.1:5173`). The UI will prompt
for character selection before connecting to the websocket backend.

## 4. Exercise the chat without the UI
If you only want to verify backend behaviour, use the helper script in
`scripts/basic_chat_cli.py`. It opens a websocket connection, sends a sample
message, and prints the character response.
```bash
python scripts/basic_chat_cli.py "Hello there!"
```
Use `--uri` to point at a custom backend address if needed.

## 5. Run the tests
```bash
pytest
```

## Troubleshooting
- Ensure the backend virtual environment is activated before running `uvicorn`.
- If you see `ModuleNotFoundError` for `fastapi` or `websockets`, reinstall the
  dependencies inside your virtual environment.
- The helper script keeps reading websocket messages until each character
  responds. If you add more characters to the payload, make sure each has a
  unique `id` so the script can track them.

Happy testing!