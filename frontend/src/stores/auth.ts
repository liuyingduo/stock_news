/**
 * 用户认证状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/api/auth'
import { getCurrentUser, login as loginApi, type LoginData } from '@/api/auth'

const TOKEN_KEY = 'auth_token'

export const useAuthStore = defineStore('auth', () => {
    // 状态
    const user = ref<UserInfo | null>(null)
    const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
    const loading = ref(false)

    // 计算属性
    const isLoggedIn = computed(() => !!token.value && !!user.value)
    const username = computed(() => user.value?.username || '')

    // 设置Token
    function setToken(newToken: string) {
        token.value = newToken
        localStorage.setItem(TOKEN_KEY, newToken)
    }

    // 清除Token
    function clearToken() {
        token.value = null
        localStorage.removeItem(TOKEN_KEY)
    }

    // 登录
    async function login(data: LoginData) {
        loading.value = true
        try {
            const response = await loginApi(data)
            setToken(response.access_token)
            await fetchUser()
            return true
        } catch (error) {
            clearToken()
            throw error
        } finally {
            loading.value = false
        }
    }

    // 登出
    function logout() {
        user.value = null
        clearToken()
    }

    // 获取用户信息
    async function fetchUser() {
        if (!token.value) return

        loading.value = true
        try {
            user.value = await getCurrentUser()
        } catch (error) {
            logout()
            throw error
        } finally {
            loading.value = false
        }
    }

    // 初始化 - 如果有token则获取用户信息
    async function init() {
        if (token.value) {
            try {
                await fetchUser()
            } catch {
                logout()
            }
        }
    }

    return {
        user,
        token,
        loading,
        isLoggedIn,
        username,
        login,
        logout,
        fetchUser,
        init,
        setToken,
        clearToken
    }
})
