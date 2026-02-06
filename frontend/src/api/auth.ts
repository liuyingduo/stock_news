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
  phone?: string
  wechat_openid?: string
  plan?: string
  plan_expires_at?: string | null
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

/**
 * 发送短信验证码
 */
export const sendSmsCode = (phone: string) => {
  return api.post('/auth/sms/send', { phone })
}

/**
 * 短信验证码登录
 */
export const loginBySms = (phone: string, code: string): Promise<TokenResponse> => {
  return api.post('/auth/sms/login', { phone, code })
}

/**
 * 获取微信扫码登录地址
 */
export const getWechatLoginUrl = (): Promise<{ url: string }> => {
  return api.get('/auth/wechat/login-url')
}

/**
 * 更新当前用户信息
 */
export const updateCurrentUser = (data: Partial<Pick<UserInfo, 'username' | 'phone'>>): Promise<UserInfo> => {
  return api.put('/auth/me', data)
}
