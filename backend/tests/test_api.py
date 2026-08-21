from fastapi.testclient import TestClient
from app.main import app  # 假设你的 FastAPI app 实例在 main.py 中

# 1. 创建全局 Client（相当于 Spring Boot 的 @AutoConfigureMockMvc）
client = TestClient(app)

# 2. 定义测试函数（相当于 @Test）
def test_chat_success():
    # 构造请求体（对应你的 ChatRequest 模型）
    request_body = {
        "message": "你好，我是小志，我想查询我的订单",
        "user_id": 1000,
        "conversation_id": "conv_1000"
    }

    # 执行 POST 请求
    response = client.post("/api/chat", json=request_body)

    # 断言（相当于 assertEquals / assertTrue）
    assert response.status_code == 200
    assert "reply" in response.json()  # 假设返回字段里有 reply

    # 打印响应体方便调试（相当于 System.out.println）
    print("响应内容1:", response.json())

    # 第二次请求
    # 构造请求体（对应你的 ChatRequest 模型）
    request_body2 = {
        "message": "你好，我的订单编号是ORD_001",
        "user_id": 1000,
        "conversation_id": "conv_1000"
    }

    # 执行 POST 请求
    response = client.post("/api/chat", json=request_body2)

    # 断言（相当于 assertEquals / assertTrue）
    assert response.status_code == 200
    assert "reply" in response.json()  # 假设返回字段里有 reply

    # 打印响应体方便调试（相当于 System.out.println）
    print("响应内容2:", response.json())

    # 第三次请求
    # 构造请求体（对应你的 ChatRequest 模型）
    request_body3 = {
        "message": "你好，我叫什么",
        "user_id": 1000,
        "conversation_id": "conv_1000"
    }

    # 执行 POST 请求
    response = client.post("/api/chat", json=request_body3)

    # 断言（相当于 assertEquals / assertTrue）
    assert response.status_code == 200
    assert "reply" in response.json()  # 假设返回字段里有 reply

    # 打印响应体方便调试（相当于 System.out.println）
    print("响应内容3:", response.json())