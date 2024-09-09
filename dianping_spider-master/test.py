import requests

# 获取私密代理IP API
api = "https://dps.kdlapi.com/api/getdps"

# 请求参数
params = {
    "secret_id": "o6fk350y1g5agx592huo",
    "signature": "bvrce60vdwx9nfqzaoj7r7oanzxhqzop",
    "num": 1,   # 提取数量
}

# 获取响应内容
response = requests.get(api, params=params)
print(response.text)