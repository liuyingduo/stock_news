import asyncio
import httpx
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000/api/auth/"

async def test_auth_flow():
    # 测试数据
    username = "test_user_001"
    email = "test001@example.com"
    password = "password123"

    async with httpx.AsyncClient() as client:
        print(f"1. 尝试注册用户: {email}")
        try:
            register_response = await client.post(
                urljoin(BASE_URL, "register"),
                json={"username": username, "email": email, "password": password}
            )
            print(f"   注册响应: {register_response.status_code}")
            if register_response.status_code == 201:
                print("   ✅ 注册成功")
            elif register_response.status_code == 400 and "已" in register_response.text:
                print("   ⚠️ 用户已存在，继续测试登录")
            else:
                print(f"   ❌ 注册失败: {register_response.text}")
                return
        except Exception as e:
            print(f"   ❌ 连接失败 (确保后端已启动): {e}")
            return

        print(f"\n2. 尝试登录用户: {email}")
        try:
            login_response = await client.post(
                urljoin(BASE_URL, "login"),
                json={"email": email, "password": password}
            )
            print(f"   登录响应: {login_response.status_code}")
            
            if login_response.status_code != 200:
                print(f"   ❌ 登录失败: {login_response.text}")
                return
            
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"   ✅ 登录成功, Token获取: {token[:20]}...")
            
        except Exception as e:
            print(f"   ❌是登录请求失败: {e}")
            return

        print(f"\n3. 使用Token获取用户信息")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            me_response = await client.get(
                urljoin(BASE_URL, "me"),
                headers=headers
            )
            print(f"   获取用户响应: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_info = me_response.json()
                print(f"   ✅ 验证成功! 当前用户: {user_info['username']} ({user_info['email']})")
            else:
                print(f"   ❌ Token验证失败: {me_response.text}")
                
        except Exception as e:
            print(f"   ❌ 获取用户信息请求失败: {e}")

if __name__ == "__main__":
    print("开始认证流程测试 (请确保后端服务在 localhost:8000 运行)")
    print("-" * 50)
    asyncio.run(test_auth_flow())
    print("-" * 50)
