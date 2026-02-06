"""认证服务 - 密码哈希和JWT处理"""
from datetime import datetime, timedelta
from typing import Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.core.database import get_database
from app.models.user import TokenData, UserResponse

# Argon2 密码哈希器（默认使用 Argon2id 变体）
ph = PasswordHasher()

# OAuth2 Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """对密码进行哈希处理（使用 Argon2id）"""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def get_user_by_email(email: str) -> Optional[dict]:
    """通过邮箱获取用户"""
    db = get_database()
    user = await db.users.find_one({"email": email})
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[UserResponse]:
    """从Token获取当前用户"""
    if not token:
        return None
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"],
        is_active=user.get("is_active", True)
    )


async def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> Optional[UserResponse]:
    """获取当前用户（可选，不会抛出异常）"""
    if not token:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None
