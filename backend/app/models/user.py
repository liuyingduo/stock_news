"""用户模型定义"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """用户注册请求"""
    username: Optional[str] = Field(None, min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    phone: Optional[str] = Field(None, description="手机号码")


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应（不含敏感信息）"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
    phone: Optional[str] = Field(None, description="手机号码")
    created_at: datetime = Field(..., description="创建时间")
    is_active: bool = Field(default=True, description="是否激活")


class UserUpdate(BaseModel):
    """用户信息更新请求"""
    username: Optional[str] = Field(None, min_length=2, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, description="手机号码")


class UserInDB(BaseModel):
    """数据库中的用户模型"""
    username: str
    email: str
    phone: Optional[str] = None
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class Token(BaseModel):
    """JWT Token响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenData(BaseModel):
    """Token解析后的数据"""
    email: Optional[str] = None
