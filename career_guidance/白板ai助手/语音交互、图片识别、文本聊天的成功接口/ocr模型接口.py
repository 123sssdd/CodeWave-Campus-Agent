import base64
import hashlib
import hmac
import json
import os
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # 允许跨域请求


class XunfeiOCR:
    def __init__(self, app_id, api_key, api_secret):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host = "cbm01.cn-huabei-1.xf-yun.com"
        self.path = "/v1/private/se75ocrbm"
        self.url = f"https://{self.host}{self.path}"

    def _get_auth_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = f"host: {self.host}\ndate: {date}\nPOST {self.path} HTTP/1.1"
        signature_sha = hmac.new(self.api_secret.encode('utf-8'),
                                 signature_origin.encode('utf-8'),
                                 hashlib.sha256).digest()
        signature = base64.b64encode(signature_sha).decode('utf-8')
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        auth_url = (
            f"{self.url}?authorization={authorization}&"
            f"host={self.host}&date={date}"
        )
        return auth_url

    def _build_request(self, image_base64, file_type="jpg"):
        request_data = {
            "header": {
                "app_id": self.app_id,
                "uid": "39769795890",
                "did": "SR082321940000200",
                "imei": "8664020318693660",
                "imsi": "4600264952729100",
                "mac": "6c:92:bf:65:c6:14",
                "net_type": "wifi",
                "net_isp": "CMCC",
                "status": 0,
                "request_id": None,
                "res_id": ""
            },
            "parameter": {
                "ocr": {
                    "result_option": "normal",
                    "result_format": "json",
                    "output_type": "one_shot",
                    "exif_option": "0",
                    "json_element_option": "",
                    "markdown_element_option": "watermark=0,page_header=0,page_footer=0,page_number=0,graph=0",
                    "sed_element_option": "watermark=0,page_header=0,page_footer=0,page_number=0,graph=0",
                    "alpha_option": "0",
                    "rotation_min_angle": 5,
                    "result": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "plain"
                    }
                }
            },
            "payload": {
                "image": {
                    "encoding": file_type,
                    "image": image_base64,
                    "status": 0,
                    "seq": 0
                }
            }
        }
        return request_data

    def _extract_text(self, data):
        if isinstance(data, dict):
            if "text" in data and isinstance(data["text"], (str, list)):
                if isinstance(data["text"], str):
                    return [data["text"]]
                else:
                    return data["text"][:1]
            for value in data.values():
                result = self._extract_text(value)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._extract_text(item)
                if result:
                    return result
        return []

    def ocr_image(self, image_data, file_type="jpg"):
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        request_data = self._build_request(image_base64, file_type)
        auth_url = self._get_auth_url()
        headers = {'Content-Type': 'application/json'}
        response = requests.post(auth_url,
                                 data=json.dumps(request_data),
                                 headers=headers)

        if response.status_code != 200:
            raise Exception(f"请求失败，状态码 {response.status_code}: {response.text}")

        result = response.json()
        if result['header']['code'] != 0:
            raise Exception(f"API错误: {result['header']['message']}")

        text = base64.b64decode(result['payload']['result']['text']).decode('utf-8')
        json_result = json.loads(text)
        all_texts = self._extract_text(json_result)
        return all_texts


# 初始化OCR实例
# 注意：实际部署时应从环境变量获取这些敏感信息
ocr = XunfeiOCR(
    app_id="4a63d497",
    api_key="10dae3cad4f9f8574a51c8c4bf74ce0c",
    api_secret="ZWU3MjEwMGM1YTQyZTQxNmRmNDBjOWJj"
)


@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400

    file = request.files['file']

    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    # 检查文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({
            "status": "error",
            "message": f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        }), 400

    try:
        # 读取文件内容
        image_data = file.read()
        # 调用OCR识别
        result = ocr.ocr_image(image_data, file_ext)
        return jsonify({
            "status": "success",
            "texts": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/ocr_base64', methods=['POST'])
def ocr_base64_endpoint():
    # 处理base64编码的图像
    data = request.get_json()
    if not data or 'image_base64' not in data:
        return jsonify({"status": "error", "message": "No base64 image provided"}), 400

    try:
        # 从base64字符串中提取文件类型和图像数据
        header, encoded = data['image_base64'].split(",", 1)
        file_ext = header.split("/")[1].split(";")[0]
        image_data = base64.b64decode(encoded)

        # 调用OCR识别
        result = ocr.ocr_image(image_data, file_ext)
        return jsonify({
            "status": "success",
            "texts": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)