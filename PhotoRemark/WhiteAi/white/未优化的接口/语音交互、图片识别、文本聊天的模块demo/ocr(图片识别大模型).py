import base64
import hashlib
import hmac
import json
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import requests


class XunfeiOCR:
    def __init__(self, app_id, api_key, api_secret):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host = "cbm01.cn-huabei-1.xf-yun.com"
        self.path = "/v1/private/se75ocrbm"
        self.url = f"https://{self.host}{self.path}"

    def _get_auth_url(self):
        # 生成RFC1123格式的日期
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 准备签名字符串
        signature_origin = f"host: {self.host}\ndate: {date}\nPOST {self.path} HTTP/1.1"

        # 计算签名
        signature_sha = hmac.new(self.api_secret.encode('utf-8'),
                                 signature_origin.encode('utf-8'),
                                 hashlib.sha256).digest()
        signature = base64.b64encode(signature_sha).decode('utf-8')

        # 准备授权信息
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

        # 构建认证URL
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
        """提取第一个有效的文本内容"""
        if isinstance(data, dict):
            if "text" in data and isinstance(data["text"], (str, list)):
                if isinstance(data["text"], str):
                    return [data["text"]]
                else:
                    return data["text"][:1]  # 只返回第一个文本
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

    def ocr_image(self, image_path):
        # 读取并编码图片
        with open(image_path, "rb") as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        file_type = image_path.split('.')[-1].lower()

        # 构建请求数据
        request_data = self._build_request(image_base64, file_type)
        auth_url = self._get_auth_url()

        # 发送请求
        headers = {'Content-Type': 'application/json'}
        response = requests.post(auth_url,
                                 data=json.dumps(request_data),
                                 headers=headers)

        if response.status_code != 200:
            raise Exception(f"请求失败，状态码 {response.status_code}: {response.text}")

        # 解析响应
        result = response.json()
        if result['header']['code'] != 0:
            raise Exception(f"API错误: {result['header']['message']}")

        # 解码base64文本结果
        text = base64.b64decode(result['payload']['result']['text']).decode('utf-8')
        json_result = json.loads(text)

        # 提取文本内容
        all_texts = self._extract_text(json_result)
        return all_texts


# 使用示例
if __name__ == "__main__":
    # 替换为你的实际凭证
    APP_ID = "4a63d497"
    API_KEY = "10dae3cad4f9f8574a51c8c4bf74ce0c"
    API_SECRET = "ZWU3MjEwMGM1YTQyZTQxNmRmNDBjOWJj"

    ocr = XunfeiOCR(APP_ID, API_KEY, API_SECRET)

    try:
        # 替换为你的图片路径
        image_path = r"../../语音交互、图片识别、文本聊天的成功接口/图片识别、语音交互测试上传的文件/图片识别示例2.png"
        result = ocr.ocr_image(image_path)
        print("图片识别的文本:")
        print("\n".join(result))
    except Exception as e:
        print(f"OCR失败: {str(e)}")