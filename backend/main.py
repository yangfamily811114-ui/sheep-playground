from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI()

# 確保路徑正確
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "mood.json")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/mood")
async def get_mood():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mood": "未知", "emoji": "❓"}

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    return """
    <html>
    <head><title>羊羊後台</title></head>
    <body style="font-family: sans-serif; padding: 50px; text-align: center;">
        <h1>🐑 羊羊秘密後台</h1>
        <p>目前暫時僅供觀察數據，未來會加入更多控制開關！</p>
        <a href="/">回到前台</a>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8686)
