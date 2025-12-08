#!/usr/bin/env python3
import requests
import json

# 测试发送私信给真实用户
url = "http://localhost:8000/api/v1/instagram/users/lucianliu6/dm"
data = {
    "username": "lucianliu6",
    "message": "Hello! Testing Instagram API from UniAPI. 🚀"
}

print("📤 发送测试私信...")
print(f"目标用户: @{data['username']}")
print(f"消息内容: {data['message']}")
print()
print("⏳ 这可能需要 10-20 秒，请等待...")
print()

try:
    response = requests.post(url, json=data, timeout=120)
    print(f"状态码: {response.status_code}")
    print()
    print("响应:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ 错误: {e}")
