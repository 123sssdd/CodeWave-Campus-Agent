# test_chat_api.py
import sys
import traceback

print("开始导入模块...")
try:
    print("导入 json...")
    import json
    print("json 导入成功")
    
    print("导入 requests...")
    import requests
    print("requests 导入成功")
    
    print("导入 Flask...")
    from flask import Flask, request, jsonify
    print("Flask 导入成功")
    
    print("导入 CORS...")
    from flask_cors import CORS
    print("CORS 导入成功")
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("详细错误信息:")
    traceback.print_exc()
    sys.exit(1)

print("创建 Flask 应用...")
app = Flask(__name__)
CORS(app)

print("设置 API 密钥...")
api_key = "Bearer IZCYjZldtFfctRDljtZJ:yGDOYHzOXQRmoKXQIRAw"
url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

print("定义路由...")
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "chat"})

if __name__ == '__main__':
    print("启动服务器...")
    app.run(host='0.0.0.0', port=5001, debug=True)