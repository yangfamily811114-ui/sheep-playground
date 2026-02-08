from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import os
import subprocess
from datetime import datetime

app = FastAPI(root_path="/playground")

# 確保路徑正確
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "mood.json")
SHOPPING_FILE = os.path.join(BASE_DIR, "shopping.json")
BADGES_FILE = os.path.join(BASE_DIR, "badges.json")
LOG_FILE = os.path.join(BASE_DIR, "activity_log.json")
EXP_DIR = os.path.join(BASE_DIR, "experiments")

# 掛載靜態文件
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/exp/{name}", response_class=HTMLResponse)
async def read_experiment(name: str):
    file_path = os.path.join(EXP_DIR, f"{name}.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>404 實驗室找不到這個項目 🐑</h1>"

@app.get("/api/experiments")
async def list_experiments():
    if not os.path.exists(EXP_DIR): return []
    # 返回不含 .html 副檔名的名稱清單
    return [f.replace(".html", "") for f in os.listdir(EXP_DIR) if f.endswith(".html")]

@app.get("/api/mood")
async def get_mood():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mood": "未知", "emoji": "❓"}

@app.get("/api/shopping")
async def get_shopping():
    if os.path.exists(SHOPPING_FILE):
        with open(SHOPPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.post("/api/shopping")
async def update_shopping(items: list):
    with open(SHOPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}

@app.get("/api/badges")
async def get_badges():
    if os.path.exists(BADGES_FILE):
        with open(BADGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.get("/api/logs")
async def get_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.post("/api/logs")
async def add_log(entry: dict):
    # entry format: {"time": "...", "event": "..."}
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    
    logs.insert(0, entry)
    logs = logs[:20] # 只保留最近 20 則
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}

@app.post("/api/call_sheep")
async def call_sheep(data: dict):
    # data format: {"user": "...", "reason": "..."}
    user = data.get("user", "未知客戶")
    reason = data.get("reason", "想找羊羊聊天")
    time_str = datetime.now().strftime("%H:%M:%S")
    
    # 1. 紀錄到實驗室日誌
    log_entry = {"time": time_str, "event": f"🔔 {user} 在網頁端呼叫了羊羊！理由：{reason}"}
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    logs.insert(0, log_entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs[:20], f, ensure_ascii=False, indent=2)

    # 2. 透過 OpenClaw 發送訊息通知 Jimmy 羊
    alert_msg = f"🔔【網頁呼叫】最高級客戶 {user} 找你喔！\n理由：{reason}\n\n羊，快去實驗室看看吧！咩～🐑"
    subprocess.run([
        "/home/yang/.npm-global/bin/openclaw", "message", "send",
        "--target", "telegram:8585740036",
        "--message", alert_msg
    ])
    
    return {"status": "ok", "message": "收到呼叫！羊羊正飛奔過去！"}

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
