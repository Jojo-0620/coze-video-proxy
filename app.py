from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import uuid
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 存储任务
tasks_store = {}

def call_jimeng_video(image_url, prompt):
    # 模拟视频生成（5分钟）
    time.sleep(300)
    return f"https://example.com/videos/{image_url.split('/')[-1]}.mp4"

def generate_video_task(task_id, image_url, prompt):
    try:
        print(f"[{datetime.now()}] 任务 {task_id} 开始生成")
        tasks_store[task_id]['status'] = 'processing'
        video_url = call_jimeng_video(image_url, prompt)
        tasks_store[task_id]['status'] = 'completed'
        tasks_store[task_id]['video_url'] = video_url
    except Exception as e:
        tasks_store[task_id]['status'] = 'failed'
        tasks_store[task_id]['error'] = str(e)

@app.route('/generate', methods=['POST'])
def generate_video():
    data = request.get_json()
    image_url = data.get('image_url')
    prompt = data.get('prompt', '')
    if not image_url:
        return jsonify({'error': '缺少image_url参数'}), 400
    task_id = str(uuid.uuid4())
    tasks_store[task_id] = {'status': 'pending'}
    thread = threading.Thread(target=generate_video_task, args=(task_id, image_url, prompt))
    thread.start()
    return jsonify({'task_id': task_id})

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    task = tasks_store.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    response = {'status': task['status']}
    if task['status'] == 'completed':
        response['video_url'] = task.get('video_url')
    elif task['status'] == 'failed':
        response['error'] = task.get('error')
    return jsonify(response)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
