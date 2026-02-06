import base64
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Literal, Optional

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException

from bson import ObjectId
from app.config import settings
from app.core.database import get_database

PLAN_CONFIG = {
    "pro": {
        "id": "pro",
        "name": "专业版",
        "monthly_price": 399,
        "annual_discount_rate": 0.2,
        "features": [
            "全量实时信息流",
            "万古经纬穿透图谱",
            "价值雷达预警",
            "无限次AI深度研报",
            "7x24h 专属客服支持",
        ],
    }
}


def get_plan(plan_id: str):
    plan = PLAN_CONFIG.get(plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="无效的订阅计划")
    return plan


def calculate_amount(plan_id: str, billing_cycle: Literal["monthly", "annual"]) -> int:
    plan = get_plan(plan_id)
    monthly_price = plan["monthly_price"]
    if billing_cycle == "monthly":
        return monthly_price
    annual_total = monthly_price * 12
    return int(round(annual_total * (1 - plan["annual_discount_rate"])))


def _load_private_key(path: str):
    with open(path, "rb") as file:
        return serialization.load_pem_private_key(file.read(), password=None)


def _load_public_key(path: str):
    with open(path, "rb") as file:
        return serialization.load_pem_public_key(file.read())


def _wechat_build_authorization(method: str, url: str, body: str):
    if not all([
        settings.wechat_mchid,
        settings.wechat_serial_no,
        settings.wechat_private_key_path,
    ]):
        raise HTTPException(status_code=500, detail="微信支付配置缺失")

    timestamp = str(int(time.time()))
    nonce_str = uuid.uuid4().hex
    message = f"{timestamp}\n{nonce_str}\n{method}\n{url}\n{body}\n"

    private_key = _load_private_key(settings.wechat_private_key_path)
    signature = base64.b64encode(
        private_key.sign(message.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
    ).decode("utf-8")

    return (
        "WECHATPAY2-SHA256-RSA2048 "
        f"mchid=\"{settings.wechat_mchid}\","
        f"serial_no=\"{settings.wechat_serial_no}\","
        f"nonce_str=\"{nonce_str}\","
        f"timestamp=\"{timestamp}\","
        f"signature=\"{signature}\""
    )


def _wechat_decrypt_resource(resource: dict) -> dict:
    if not settings.wechat_api_v3_key:
        raise HTTPException(status_code=500, detail="微信支付配置缺失")

    api_v3_key = settings.wechat_api_v3_key.encode("utf-8")
    aesgcm = AESGCM(api_v3_key)
    ciphertext = base64.b64decode(resource["ciphertext"])
    nonce = resource["nonce"].encode("utf-8")
    associated_data = resource.get("associated_data")
    associated_bytes = associated_data.encode("utf-8") if associated_data else None

    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_bytes)
    return json.loads(plaintext.decode("utf-8"))


def _alipay_sign(params: dict) -> str:
    if not settings.alipay_private_key_path:
        raise HTTPException(status_code=500, detail="支付宝配置缺失")

    unsigned_items = [f"{k}={v}" for k, v in sorted(params.items()) if v is not None and v != ""]
    unsigned_string = "&".join(unsigned_items)
    private_key = _load_private_key(settings.alipay_private_key_path)
    signature = private_key.sign(unsigned_string.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(signature).decode("utf-8")


def _alipay_verify(params: dict, signature: str) -> bool:
    if not settings.alipay_public_key_path:
        raise HTTPException(status_code=500, detail="支付宝配置缺失")

    verify_params = {k: v for k, v in params.items() if k not in {"sign", "sign_type"}}
    unsigned_items = [f"{k}={v}" for k, v in sorted(verify_params.items()) if v is not None and v != ""]
    unsigned_string = "&".join(unsigned_items)
    public_key = _load_public_key(settings.alipay_public_key_path)
    try:
        public_key.verify(
            base64.b64decode(signature),
            unsigned_string.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


async def wechat_native_pay(out_trade_no: str, description: str, amount_fen: int) -> str:
    if not all([
        settings.wechat_mchid,
        settings.wechat_appid,
        settings.wechat_notify_url,
        settings.wechat_private_key_path,
        settings.wechat_serial_no,
    ]):
        raise HTTPException(status_code=500, detail="微信支付配置缺失")

    url_path = "/v3/pay/transactions/native"
    payload = {
        "appid": settings.wechat_appid,
        "mchid": settings.wechat_mchid,
        "description": description,
        "out_trade_no": out_trade_no,
        "notify_url": settings.wechat_notify_url,
        "amount": {
            "total": amount_fen,
            "currency": "CNY",
        },
    }

    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    authorization = _wechat_build_authorization("POST", url_path, body)

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"https://api.mch.weixin.qq.com{url_path}",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": authorization,
            },
            content=body,
        )

    if response.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"微信支付下单失败: {response.text}")

    data = response.json()
    code_url = data.get("code_url")
    if not code_url:
        raise HTTPException(status_code=502, detail="微信支付未返回二维码")

    return code_url


async def alipay_precreate(out_trade_no: str, subject: str, amount_yuan: int) -> str:
    if not all([
        settings.alipay_app_id,
        settings.alipay_private_key_path,
        settings.alipay_notify_url,
    ]):
        raise HTTPException(status_code=500, detail="支付宝配置缺失")

    params = {
        "app_id": settings.alipay_app_id,
        "method": "alipay.trade.precreate",
        "format": "JSON",
        "charset": "utf-8",
        "sign_type": "RSA2",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "notify_url": settings.alipay_notify_url,
        "biz_content": json.dumps(
            {
                "out_trade_no": out_trade_no,
                "total_amount": f"{amount_yuan:.2f}",
                "subject": subject,
            },
            separators=(",", ":"),
            ensure_ascii=False,
        ),
    }

    params["sign"] = _alipay_sign(params)

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post("https://openapi.alipay.com/gateway.do", data=params)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"支付宝下单失败: {response.text}")

    data = response.json().get("alipay_trade_precreate_response", {})
    if data.get("code") != "10000":
        raise HTTPException(status_code=502, detail=f"支付宝下单失败: {data.get('sub_msg')}")

    qr_code = data.get("qr_code")
    if not qr_code:
        raise HTTPException(status_code=502, detail="支付宝未返回二维码")

    return qr_code


async def create_payment_order(
    user_id: str,
    user_email: str,
    plan_id: str,
    billing_cycle: Literal["monthly", "annual"],
    channel: Literal["wechat", "alipay"],
):
    plan = get_plan(plan_id)
    amount = calculate_amount(plan_id, billing_cycle)
    out_trade_no = f"WGJW{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

    order_doc = {
        "user_id": ObjectId(user_id),
        "user_email": user_email,
        "plan_id": plan_id,
        "billing_cycle": billing_cycle,
        "channel": channel,
        "amount": amount,
        "currency": "CNY",
        "out_trade_no": out_trade_no,
        "status": "pending",
        "qr_code_url": "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    db = get_database()
    result = await db.payment_orders.insert_one(order_doc)

    description = f"万古经纬 {plan['name']}（{'年付' if billing_cycle == 'annual' else '月付'}）"

    if channel == "wechat":
        code_url = await wechat_native_pay(out_trade_no, description, amount * 100)
    else:
        code_url = await alipay_precreate(out_trade_no, description, amount)

    await db.payment_orders.update_one(
        {"_id": result.inserted_id},
        {"$set": {"qr_code_url": code_url, "updated_at": datetime.utcnow()}},
    )

    order_doc["_id"] = result.inserted_id
    order_doc["qr_code_url"] = code_url

    return order_doc


async def get_order_by_id(order_id: str) -> Optional[dict]:
    db = get_database()
    return await db.payment_orders.find_one({"_id": ObjectId(order_id)})


async def get_order_by_out_trade_no(out_trade_no: str) -> Optional[dict]:
    db = get_database()
    return await db.payment_orders.find_one({"out_trade_no": out_trade_no})


async def mark_order_paid(out_trade_no: str, transaction_id: Optional[str] = None):
    db = get_database()
    order = await db.payment_orders.find_one({"out_trade_no": out_trade_no})
    if not order or order.get("status") == "paid":
        return order

    now = datetime.utcnow()
    await db.payment_orders.update_one(
        {"out_trade_no": out_trade_no},
        {"$set": {"status": "paid", "paid_at": now, "transaction_id": transaction_id, "updated_at": now}},
    )

    user = await db.users.find_one({"_id": order["user_id"]})
    if user:
        expires_at = user.get("plan_expires_at")
        base_time = expires_at if isinstance(expires_at, datetime) and expires_at > now else now
        duration = timedelta(days=30 if order["billing_cycle"] == "monthly" else 365)
        new_expires = base_time + duration

        await db.users.update_one(
            {"_id": order["user_id"]},
            {"$set": {"plan": order["plan_id"], "plan_expires_at": new_expires}},
        )

    return order


async def handle_wechat_notify(payload: dict):
    resource = payload.get("resource")
    if not resource:
        raise HTTPException(status_code=400, detail="无效通知")

    data = _wechat_decrypt_resource(resource)
    out_trade_no = data.get("out_trade_no")
    trade_state = data.get("trade_state")

    if trade_state == "SUCCESS" and out_trade_no:
        await mark_order_paid(out_trade_no, data.get("transaction_id"))


async def handle_alipay_notify(params: dict):
    signature = params.get("sign")
    if not signature:
        raise HTTPException(status_code=400, detail="无效通知")

    if not _alipay_verify(params, signature):
        raise HTTPException(status_code=400, detail="签名校验失败")

    trade_status = params.get("trade_status")
    out_trade_no = params.get("out_trade_no")
    if trade_status in {"TRADE_SUCCESS", "TRADE_FINISHED"} and out_trade_no:
        await mark_order_paid(out_trade_no, params.get("trade_no"))
