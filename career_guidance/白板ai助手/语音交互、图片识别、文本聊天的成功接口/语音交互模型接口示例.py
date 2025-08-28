import requests
import json


def test_voice_api(audio_file_path, api_url="http://localhost:7000/chat"):
    """
    语音接口测试函数，按要求格式输出结果
    :param audio_file_path: 要上传的语音文件路径
    :param api_url: 接口地址，默认为本地7000端口
    """
    try:
        # 打开音频文件
        with open(audio_file_path, 'rb') as f:
            files = {'audio': f}
            response = requests.post(api_url, files=files)

        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            if 'audio_file' in result:
                print(f"测试成功，回复的音频文件：{result['audio_file']}")
                return True
            else:
                print("测试失败：响应中没有包含音频文件路径")
                return False
        else:
            print(f"测试失败：接口返回状态码 {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"测试失败：请求发送失败 - {str(e)}")
        return False
    except Exception as e:
        print(f"测试失败：发生错误 - {str(e)}")
        return False


if __name__ == "__main__":
    # 替换为你要测试的音频文件路径
    audio_file = r"图片识别、语音交互测试上传的文件/语音交互示例语音2.wav"

    # 调用测试函数
    test_voice_api(audio_file)