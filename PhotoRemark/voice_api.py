import base64
import hashlib
import hmac
import json
import os
import threading
import time
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from websocket import create_connection
from pydub import AudioSegment
from flask import Flask, request, jsonify
import uuid
from flask_cors import CORS  # 导入CORS

app = Flask(__name__)
CORS(app)  # 启用CORS


# 配置信息
app_id = "4a63d497"
Key = "10dae3cad4f9f8574a51c8c4bf74ce0c"
Secret = "ZWU3MjEwMGM1YTQyZTQxNmRmNDBjOWJj"
scene = "sos_app"  # 默认固定值
base_url = "ws://sparkos.xfyun.cn/v1/openapi/chat"

# 音频输出目录
audio_output_dir = "语音交互回复音频"
os.makedirs(audio_output_dir, exist_ok=True)


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


def assemble_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }
    return requset_url + "?" + urlencode(values)


def send_data(ws, audio_data):
    count = 0
    status = 0
    headerstatus = 0

    for i in range(0, len(audio_data), 1280):
        data = audio_data[i:i + 1280]

        if count == 0:
            status = 0
        elif len(data) == 1280:
            headerstatus = 1
            status = 1
        else:
            headerstatus = 1
            status = 2

        count += 1
        content_b64 = base64.b64encode(data).decode()

        data = {
            "header": {
                "app_id": app_id,
                "uid": str(uuid.uuid4()),
                "status": headerstatus,
                "stmid": "1",
                "scene": "sos_app",
                "msc.lat": 19.65309164062,
                "msc.lng": 109.259056086,
                "interact_mode": "continuous_vad"
            },
            "parameter": {
                "iat": {
                    "iat": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    },
                },
                "nlp": {
                    "nlp": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    },
                    "new_session": "global"
                },
                "tts": {
                    "vcn": "x5_lingxiaoyue_flow",
                    "speed": 50,
                    "volume": 50,
                    "pitch": 50,
                    "tts": {
                        "encoding": "lame",
                        "sample_rate": 16000,
                        "channels": 1,
                        "bit_depth": 16,
                        "frame_size": 0
                    }
                },
            },
            "payload": {
                "audio": {
                    "status": status,
                    "audio": content_b64,
                    "encoding": "raw",
                    "sample_rate": 16000,
                    "channels": 1,
                    "bit_depth": 16,
                    "frame_size": 0
                },
            }
        }
        data_js = json.dumps(data)
        ws.send(data_js)
        time.sleep(0.04)


def recv_data(ws):
    audio_array = []
    text_response = ""

    while True:
        result = ws.recv()
        result_js = json.loads(result)

        if result_js['header']['code'] == 0 and 'payload' in result_js:
            if 'event' in result_js['payload']:
                decoded_bytes = base64.b64decode(result_js['payload']['event']['text'])
                text_response = decoded_bytes.decode('utf-8')
            elif 'iat' in result_js['payload']:
                decoded_bytes = base64.b64decode(result_js['payload']['iat']['text'])
                text_response = decoded_bytes.decode('utf-8')
            elif 'nlp' in result_js['payload']:
                decoded_bytes = base64.b64decode(result_js['payload']['nlp']['text'])
                text_response = decoded_bytes.decode('utf-8')
            elif 'tts' in result_js['payload']:
                if len(result_js['payload']['tts']['audio']) > 0:
                    audio_bytes = base64.b64decode(result_js['payload']['tts']['audio'])
                    audio_array.append(audio_bytes)
                try:
                    status = result_js["payload"]["tts"]["status"]
                    if status == 2:
                        audio_file = write_audio_file(audio_array)
                        return {"text": text_response, "audio_file": audio_file}
                except:
                    pass


def write_audio_file(audio_array):
    time_now = str(int(time.time()))
    file_name = f"{audio_output_dir}/response_{time_now}.mp3"

    with open(file_name, "wb+") as fp:
        for audio in audio_array:
            fp.write(audio)

    return file_name


@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 获取前端发送的音频数据
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['audio']
        audio_data = audio_file.read()

        # 建立WebSocket连接
        path = assemble_auth_url(requset_url=base_url, method="GET", api_key=Key, api_secret=Secret)
        ws = create_connection(path)

        # 使用共享变量存储结果
        result = None

        def wrapper(ws):
            nonlocal result
            result = recv_data(ws)

        # 创建发送和接收线程
        thread_send = threading.Thread(target=send_data, args=(ws, audio_data))
        thread_recv = threading.Thread(target=wrapper, args=(ws,))

        thread_recv.start()
        thread_send.start()

        thread_recv.join()
        thread_send.join()

        # 关闭WebSocket连接
        ws.close()

        # 返回结果给前端
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "No response received"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "voice"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)