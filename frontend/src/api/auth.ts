/**
 * 认证相关API接口封装
 */
import api from './index'

// 类型定义
export interface RegisterData {
  username?: string // 用户名改为可选
  email: string
  password: string
  phone?: string // 新增手机号
}

export interface LoginData {
  email: string
  password: string
}

export interface UserInfo {
  id: string
  username: string
  email: string
  created_at: string
  is_active: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

/**
 * 用户注册
 */
export const register = (data: RegisterData): Promise<UserInfo> => {
  return api.post('/auth/register', data)
}

/**
 * 用户登录
 */
export const login = (data: LoginData): Promise<TokenResponse> => {
  return api.post('/auth/login', data)
}

/**
 * 获取当前用户信息
 */
export const getCurrentUser = (): Promise<UserInfo> => {
  return api.get('/auth/me')
}
