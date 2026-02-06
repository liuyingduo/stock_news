import random
from datetime import datetime, timedelta
from fastapi import HTTPException
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20210111 import sms_client, models

from app.config import settings
from app.core.database import get_database


def _ensure_sms_config():
    if not all([
        settings.tencent_sms_secret_id,
        settings.tencent_sms_secret_key,
        settings.tencent_sms_app_id,
        settings.tencent_sms_sign_name,
        settings.tencent_sms_template_id,
    ]):
        raise HTTPException(status_code=500, detail="短信服务配置缺失")


def _build_client():
    cred = credential.Credential(settings.tencent_sms_secret_id, settings.tencent_sms_secret_key)
    http_profile = HttpProfile()
    http_profile.endpoint = "sms.tencentcloudapi.com"
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    return sms_client.SmsClient(cred, "ap-guangzhou", client_profile)


def normalize_phone(phone: str) -> str:
    phone_digits = "".join(filter(str.isdigit, phone))
    if len(phone_digits) < 10:
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    return phone_digits


def generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


async def send_sms_code(phone: str) -> None:
    _ensure_sms_config()
    normalized = normalize_phone(phone)

    db = get_database()
    now = datetime.utcnow()

    last_record = await db.sms_codes.find_one({"phone": normalized}, sort=[("created_at", -1)])
    if last_record and (now - last_record["created_at"]).total_seconds() < 60:
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")

    code = generate_code()

    client = _build_client()
    req = models.SendSmsRequest()
    req.SmsSdkAppId = settings.tencent_sms_app_id
    req.SignName = settings.tencent_sms_sign_name
    req.TemplateId = settings.tencent_sms_template_id
    req.TemplateParamSet = [code]
    req.PhoneNumberSet = [f"{settings.tencent_sms_country_code}{normalized}"]

    resp = client.SendSms(req)
    status = resp.SendStatusSet[0] if resp.SendStatusSet else None
    if not status or status.Code != "Ok":
        raise HTTPException(status_code=502, detail=f"短信发送失败: {status.Message if status else 'unknown'}")

    await db.sms_codes.insert_one({
        "phone": normalized,
        "code": code,
        "created_at": now,
        "expires_at": now + timedelta(minutes=5),
        "used": False,
    })


async def verify_sms_code(phone: str, code: str) -> None:
    normalized = normalize_phone(phone)
    db = get_database()
    record = await db.sms_codes.find_one({"phone": normalized}, sort=[("created_at", -1)])

    if not record:
        raise HTTPException(status_code=400, detail="验证码不存在或已过期")

    if record.get("used"):
        raise HTTPException(status_code=400, detail="验证码已使用")

    if record.get("expires_at") and record["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="验证码已过期")

    if record.get("code") != code:
        raise HTTPException(status_code=400, detail="验证码错误")

    await db.sms_codes.update_one({"_id": record["_id"]}, {"$set": {"used": True}})
