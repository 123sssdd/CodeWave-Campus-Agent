import requests
import base64
import os
from tqdm import tqdm


class OCRClient:
    def __init__(self, base_url="http://localhost:6000"):
        self.base_url = base_url

    def _print_result(self, texts):
        """打印识别结果"""
        if not texts:
            print("未识别到文字")
            return

        print("\n识别结果:")
        print("-" * 50)
        for i, text in enumerate(texts, 1):
            print(f"{i}. {text}")
        print("-" * 50)

    def upload_image(self, image_path):
        """
        通过文件上传方式识别图片
        :param image_path: 图片路径
        """
        if not os.path.exists(image_path):
            print(f"文件不存在: {image_path}")
            return

        print(f"\n正在上传文件识别: {image_path}")

        try:
            with open(image_path, 'rb') as f, tqdm(
                    unit='B', unit_scale=True, unit_divisor=1024,
                    miniters=1, desc="上传进度"
            ) as pbar:
                # 使用回调函数显示上传进度
                def read_chunks(chunk_size=1024):
                    while True:
                        data = f.read(chunk_size)
                        if not data:
                            break
                        pbar.update(len(data))
                        yield data

                files = {'file': (os.path.basename(image_path), read_chunks())}
                response = requests.post(f"{self.base_url}/ocr", files=files)

            result = response.json()
            if result['status'] == 'success':
                self._print_result(result['texts'])
            else:
                print(f"识别失败: {result['message']}")

        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {str(e)}")
        except Exception as e:
            print(f"发生错误: {str(e)}")

    def base64_image(self, image_path):
        """
        通过Base64方式识别图片
        :param image_path: 图片路径
        """
        if not os.path.exists(image_path):
            print(f"文件不存在: {image_path}")
            return

        print(f"\n正在Base64编码识别: {image_path}")

        try:
            # 读取文件并显示进度
            file_size = os.path.getsize(image_path)
            with open(image_path, 'rb') as f, tqdm(
                    total=file_size, unit='B',
                    unit_scale=True, desc="读取进度"
            ) as pbar:
                image_data = bytearray()
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    image_data.extend(chunk)
                    pbar.update(len(chunk))

            # 获取文件扩展名
            file_ext = image_path.split('.')[-1].lower()
            if file_ext == 'jpg':
                file_ext = 'jpeg'

            # 编码并发送
            print("正在编码和识别...")
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            base64_str = f"data:image/{file_ext};base64,{image_base64}"

            response = requests.post(
                f"{self.base_url}/ocr_base64",
                json={'image_base64': base64_str},
                headers={'Content-Type': 'application/json'}
            )

            result = response.json()
            if result['status'] == 'success':
                self._print_result(result['texts'])
            else:
                print(f"识别失败: {result['message']}")

        except Exception as e:
            print(f"发生错误: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    ocr = OCRClient()

    # 测试图片路径
    test_images = [
        r"E:\OneDrive\Desktop\python项目\白板ai助手\语音交互、图片识别、文本聊天的成功接口\图片识别示例2.png",
        r"E:\OneDrive\Desktop\python项目\白板ai助手\语音交互、图片识别、文本聊天的成功接口\图片识别示例1.jpg",
        "non_existent_image.jpg"  # 不存在的图片，用于测试错误处理
    ]

    # 测试文件上传方式
    print("=" * 50)
    print("测试文件上传方式")
    print("=" * 50)
    for img in test_images:
        ocr.upload_image(img)

    # 测试Base64方式
    print("\n" + "=" * 50)
    print("测试Base64编码方式")
    print("=" * 50)
    for img in test_images[:2]:  # 只测试前两个存在的图片
        ocr.base64_image(img)