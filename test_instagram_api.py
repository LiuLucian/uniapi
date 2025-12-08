#!/usr/bin/env python3
"""
Instagram API 测试脚本
Test Instagram API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/instagram"

def test_health():
    """测试健康检查"""
    print("\n1️⃣ 测试健康检查 (Health Check)")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_user(username="instagram"):
    """测试获取用户资料"""
    print(f"\n2️⃣ 测试获取用户资料 (Get User Profile: @{username})")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/users/{username}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    # 检查是否需要配置 sessionid
    if data.get('bio') is None or data.get('followers') is None:
        print("\n⚠️  注意: bio 和 followers 为 null")
        print("需要配置 Instagram sessionid 才能获取完整数据")
        print("请查看: platforms_auth.json")

    return response.status_code == 200

def test_create_post():
    """测试创建帖子 (需要 sessionid)"""
    print("\n3️⃣ 测试创建帖子 (Create Post)")
    print("=" * 50)

    payload = {
        "caption": "测试帖子 - Test post from UniAPI #test",
        "image_path": "/path/to/test/image.jpg"
    }

    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("⏭️  跳过实际发送 (需要配置 sessionid 和真实图片路径)")
    print("配置完成后可以取消注释下方代码进行测试:")
    print("""
    # response = requests.post(f"{BASE_URL}/media", json=payload)
    # print(f"Status: {response.status_code}")
    # print(f"Response: {json.dumps(response.json(), indent=2)}")
    """)

def test_send_dm():
    """测试发送私信 (需要 sessionid)"""
    print("\n4️⃣ 测试发送私信 (Send DM)")
    print("=" * 50)

    username = "testuser"
    payload = {
        "username": username,
        "message": "Hello from UniAPI!"
    }

    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("⏭️  跳过实际发送 (需要配置 sessionid)")
    print("配置完成后可以取消注释下方代码进行测试:")
    print(f"""
    # response = requests.post(f"{BASE_URL}/users/{username}/dm", json=payload)
    # print(f"Status: {{response.status_code}}")
    # print(f"Response: {{json.dumps(response.json(), indent=2)}}")
    """)

def main():
    print("=" * 50)
    print("Instagram API 测试")
    print("=" * 50)

    # 测试基础功能
    health_ok = test_health()
    user_ok = test_get_user("instagram")

    # 说明需要配置的功能
    test_create_post()
    test_send_dm()

    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结 (Test Summary)")
    print("=" * 50)
    print(f"✅ Health Check: {'通过' if health_ok else '失败'}")
    print(f"✅ Get User Profile: {'通过' if user_ok else '失败'} (部分数据需要 sessionid)")
    print(f"⏭️  Create Post: 需要配置 sessionid")
    print(f"⏭️  Send DM: 需要配置 sessionid")

    print("\n" + "=" * 50)
    print("🔧 配置 Instagram sessionid 步骤:")
    print("=" * 50)
    print("1. 打开 Instagram 网页: https://www.instagram.com")
    print("2. 登录你的 Instagram 账号")
    print("3. 打开开发者工具 (F12)")
    print("4. 进入: Application → Cookies → https://www.instagram.com")
    print("5. 找到名为 'sessionid' 的 cookie")
    print("6. 复制 cookie 的值")
    print("7. 编辑文件: backend/platforms_auth.json")
    print("8. 替换 'YOUR_INSTAGRAM_SESSIONID_HERE' 为你复制的值")
    print("9. 重启服务器: ./stop.sh && ./start.sh")
    print("10. 再次运行此测试脚本")

    print("\n✅ Instagram API 结构完整，等待配置 sessionid 进行完整测试")

if __name__ == "__main__":
    main()
