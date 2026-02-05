"""认证路由 - 注册、登录、获取当前用户"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.database import get_database
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    get_current_user,
    get_user_by_email
)
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])


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
        "is_active": True
    }
    
    result = await db.users.insert_one(user_doc)
    
    return UserResponse(
        id=str(result.inserted_id),
        username=user_doc["username"],
        email=user_doc["email"],
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
