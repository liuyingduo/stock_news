"""认证路由 - 注册、登录、获取当前用户"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import secrets
import httpx
from urllib.parse import urlencode
from app.core.database import get_database
from app.models.user import UserCreate, UserLogin, UserResponse, UserUpdate, Token
from app.services.auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    get_current_user,
    get_user_by_email
)
from app.services.sms_service import send_sms_code, verify_sms_code, normalize_phone
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])


class SmsSendRequest(BaseModel):
    phone: str


class SmsLoginRequest(BaseModel):
    phone: str
    code: str


class WechatLoginUrlResponse(BaseModel):
    url: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """用户注册"""
    db = get_database()
    
    # 检查邮箱是否已存在
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 处理用户名
    username = user_data.username
    if not username:
        # 如果未提供用户名，使用邮箱前缀
        username = user_data.email.split("@")[0]
    
    # 检查用户名是否已存在
    existing_username = await db.users.find_one({"username": username})
    if existing_username:
        if not user_data.username:
            # 如果是自动生成的用户名重复，则添加随机后缀
            import random
            username = f"{username}_{random.randint(1000, 9999)}"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用"
            )

    # 创建用户
    user_doc = {
        "username": username,
        "email": user_data.email,
        "phone": user_data.phone,
        "hashed_password": hash_password(user_data.password),
        "created_at": datetime.utcnow(),
        "plan": "free",
        "plan_expires_at": None,
        "is_active": True
    }
    
    result = await db.users.insert_one(user_doc)
    
    return UserResponse(
        id=str(result.inserted_id),
        username=user_doc["username"],
        email=user_doc["email"],
        phone=user_doc.get("phone"),
        wechat_openid=user_doc.get("wechat_openid"),
        plan=user_doc.get("plan", "free"),
        plan_expires_at=user_doc.get("plan_expires_at"),
        created_at=user_doc["created_at"],
        is_active=user_doc["is_active"]
    )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """用户登录"""
    # 查找用户
    user = await get_user_by_email(user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户状态
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/sms/send")
async def send_sms(request: SmsSendRequest):
    await send_sms_code(request.phone)
    return {"message": "验证码已发送"}


@router.post("/sms/login", response_model=Token)
async def sms_login(request: SmsLoginRequest):
    await verify_sms_code(request.phone, request.code)

    db = get_database()
    phone = normalize_phone(request.phone)
    user = await db.users.find_one({"phone": phone})

    if not user:
        base_username = f"user_{phone[-4:]}"
        username = base_username
        exists = await db.users.find_one({"username": username})
        if exists:
            username = f"{base_username}_{secrets.randbelow(10000)}"

        email = f"{phone}@sms.local"
        user_doc = {
            "username": username,
            "email": email,
            "phone": phone,
            "hashed_password": hash_password(secrets.token_urlsafe(16)),
            "created_at": datetime.utcnow(),
            "plan": "free",
            "plan_expires_at": None,
            "is_active": True,
        }
        result = await db.users.insert_one(user_doc)
        user = {**user_doc, "_id": result.inserted_id}

    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账户已被禁用")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/wechat/login-url", response_model=WechatLoginUrlResponse)
async def wechat_login_url():
    if not all([
        settings.wechat_open_appid,
        settings.wechat_open_redirect_uri,
    ]):
        raise HTTPException(status_code=500, detail="微信登录配置缺失")

    state = secrets.token_urlsafe(16)
    db = get_database()
    await db.wechat_login_states.insert_one({
        "state": state,
        "created_at": datetime.utcnow(),
        "used": False,
    })

    params = {
        "appid": settings.wechat_open_appid,
        "redirect_uri": settings.wechat_open_redirect_uri,
        "response_type": "code",
        "scope": "snsapi_login",
        "state": state,
    }
    url = f"https://open.weixin.qq.com/connect/qrconnect?{urlencode(params)}#wechat_redirect"
    return WechatLoginUrlResponse(url=url)


@router.get("/wechat/callback")
async def wechat_callback(code: str, state: str):
    if not all([
        settings.wechat_open_appid,
        settings.wechat_open_secret,
        settings.wechat_open_redirect_uri,
        settings.frontend_base_url,
    ]):
        raise HTTPException(status_code=500, detail="微信登录配置缺失")

    db = get_database()
    record = await db.wechat_login_states.find_one({"state": state})
    if not record or record.get("used"):
        raise HTTPException(status_code=400, detail="无效的登录请求")

    await db.wechat_login_states.update_one({"_id": record["_id"]}, {"$set": {"used": True}})

    async with httpx.AsyncClient(timeout=10) as client:
        token_resp = await client.get(
            "https://api.weixin.qq.com/sns/oauth2/access_token",
            params={
                "appid": settings.wechat_open_appid,
                "secret": settings.wechat_open_secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )

    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    openid = token_data.get("openid")

    if not access_token or not openid:
        raise HTTPException(status_code=400, detail="微信授权失败")

    async with httpx.AsyncClient(timeout=10) as client:
        userinfo_resp = await client.get(
            "https://api.weixin.qq.com/sns/userinfo",
            params={
                "access_token": access_token,
                "openid": openid,
                "lang": "zh_CN",
            },
        )

    userinfo = userinfo_resp.json()
    nickname = userinfo.get("nickname") or "微信用户"

    user = await db.users.find_one({"wechat_openid": openid})
    if not user:
        base_username = nickname.replace(" ", "")[:20] or "wx_user"
        username = base_username
        exists = await db.users.find_one({"username": username})
        if exists:
            username = f"{base_username}_{secrets.randbelow(10000)}"

        email = f"wx_{openid}@wechat.local"
        user_doc = {
            "username": username,
            "email": email,
            "phone": None,
            "wechat_openid": openid,
            "hashed_password": hash_password(secrets.token_urlsafe(16)),
            "created_at": datetime.utcnow(),
            "plan": "free",
            "plan_expires_at": None,
            "is_active": True,
        }
        result = await db.users.insert_one(user_doc)
        user = {**user_doc, "_id": result.inserted_id}

    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账户已被禁用")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    jwt_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires,
    )

    redirect_url = f"{settings.frontend_base_url}/login?token={jwt_token}"
    return RedirectResponse(url=redirect_url)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """获取当前登录用户信息"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    """更新当前登录用户信息"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = get_database()
    update_fields = {}

    if update_data.username is not None and update_data.username != current_user.username:
        existing_username = await db.users.find_one({"username": update_data.username})
        if existing_username and str(existing_username.get("_id")) != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用"
            )
        update_fields["username"] = update_data.username

    if update_data.phone is not None:
        update_fields["phone"] = update_data.phone

    if update_fields:
        await db.users.update_one({"email": current_user.email}, {"$set": update_fields})

    user = await db.users.find_one({"email": current_user.email})
    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        phone=user.get("phone"),
        wechat_openid=user.get("wechat_openid"),
        plan=user.get("plan", "free"),
        plan_expires_at=user.get("plan_expires_at"),
        created_at=user["created_at"],
        is_active=user.get("is_active", True)
    )
