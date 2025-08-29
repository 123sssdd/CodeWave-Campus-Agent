from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests

APPId = "4a63d497"  # 控制台获取
APISecret = "ZWU3MjEwMGM1YTQyZTQxNmRmNDBjOWJj"  # 控制台获取
APIKey = "10dae3cad4f9f8574a51c8c4bf74ce0c"  # 控制台获取

with open("../语音交互、图片识别、文本聊天的成功接口/图片识别、语音交互测试上传的文件/图片识别示例1.jpg", "rb") as f:
    imageBytes = f.read()

class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg

class Url:
    def __init__(self, host, path, schema):
        self.host = host
        self.path = path
        self.schema = schema
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

def assemble_ws_auth_url(requset_url, method="POST", api_key="", api_secret=""):
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

url = 'https://api.xf-yun.com/v1/private/sf8e6aca1'

body = {
    "header": {
        "app_id": APPId,
        "status": 3
    },
    "parameter": {
        "sf8e6aca1": {
            "category": "ch_en_public_cloud",
            "result": {
                "encoding": "utf8",
                "compress": "raw",
                "format": "json"
            }
        }
    },
    "payload": {
        "sf8e6aca1_data_1": {
            "encoding": "jpg",
            "image": str(base64.b64encode(imageBytes), 'UTF-8'),
            "status": 3
        }
    }
}

request_url = assemble_ws_auth_url(url, "POST", APIKey, APISecret)

headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'app_id': APPId}
response = requests.post(request_url, data=json.dumps(body), headers=headers)

tempResult = json.loads(response.content.decode())
finalResult = base64.b64decode(tempResult['payload']['result']['text']).decode()

# 解析JSON并提取文字内容
ocr_data = json.loads(finalResult)
text_content = []

for page in ocr_data["pages"]:
    for line in page["lines"]:
        for word in line["words"]:
            text_content.append(word["content"])

# 合并所有识别到的文字
result_text = "".join(text_content)
print("识别到的文字内容：")
print(result_text)