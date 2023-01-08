import os
from datetime import datetime
from flask import Flask, request
import json
from subprocess import Popen
from notifypy import Notify


port = os.environ.get("port", 5001)
user_name = os.environ.get("username", "wj-Mcat")
smee_id = "https://smee.io/IwufYyRT2Y7REdJf"

p = Popen(f'smee -u {smee_id} -t http://127.0.0.1:5001/event'.split())

def read_json(file: str):
    import os
    if not os.path.exists(file):
        return None
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_json(data, file_name):
    with open(file_name, "w", encoding="utf-8") as w:
        w.write(json.dumps(data, ensure_ascii=False, indent=4) + "\n")


app = Flask(__name__)


def handle_assign(payload: dict):
    if payload['action'] == "assigned":
        if "issue" in payload:
            notification = Notify()
            number = payload['issue']['number']
            notification.title = f"Issue #{number} 任务被 assign 给你了"
            notification.message = payload['issue']['title']
            notification.send()


@app.route("/event", methods=['POST', 'GET'])
def receive_events():
    json = request.get_json()

    # 1. check if it's target repo
    if json['repository']['full_name'] != "PaddlePaddle/PaddleNLP":
        return "ok"
    
    path_dir = f".wechaty/github_events/{datetime.now().timestamp()}.json"
    save_json(json, path_dir)
    handle_assign(json)

    return 'ok'

app.run(port=5001) 