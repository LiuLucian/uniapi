#!/usr/bin/env python3
import requests
import json

# 测试发送私信
url = "http://localhost:8000/api/v1/instagram/users/instagram/dm"
data = {
    "username": "instagram",
    "message": "Hello! This is a test message from UniAPI."
}

print("📤 发送测试私信...")
print(f"目标用户: @{data['username']}")
print(f"消息内容: {data['message']}")
print()

response = requests.post(url, json=data, timeout=120)
print(f"状态码: {response.status_code}")
print()
print("响应:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
