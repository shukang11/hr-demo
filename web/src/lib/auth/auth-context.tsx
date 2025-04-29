import { User, AuthState } from "../types";
import { createContext, useContext, useEffect, useState } from "react";
import { clearToken, getToken, setToken } from "../api/client";
import { AuthApi } from "../api/auth";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

interface AuthContextType extends AuthState {
    login: (username: string, password: string, remember?: boolean) => Promise<void>;
    logout: () => Promise<void>;
    checkAuth: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 存储记住我状态的键名
const REMEMBER_ME_KEY = "hr_remember_me";

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [state, setState] = useState<AuthState>({
        isAuthenticated: false,
        user: null,
        token: getToken(),
        loading: true,
        error: null,
    });

    const navigate = useNavigate();
    const { toast } = useToast();

    // 登录方法
    const login = async (username: string, password: string, remember: boolean = false) => {
        setState(prev => ({ ...prev, loading: true, error: null }));

        try {
            const passwordHash = password; // 在实际应用中，应该使用SHA-256等算法进行哈希处理
            const response = await AuthApi.login(username, passwordHash);

            if (response.data) {
                const { token, user } = response.data;
                setToken(token);

                // 保存记住我的状态
                if (remember) {
                    localStorage.setItem(REMEMBER_ME_KEY, "true");
                } else {
                    localStorage.removeItem(REMEMBER_ME_KEY);
                }

                // 首先更新状态，设置 isAuthenticated 为 true
                setState({
                    isAuthenticated: true,
                    user,
                    token,
                    loading: false,
                    error: null,
                });

                // 显示成功提示
                toast({
                    title: "登录成功",
                    description: `欢迎回来，${user.username}！`,
                });

                // 使用 setTimeout 避免立即导航引起的渲染冲突
                setTimeout(() => {
                    // 获取之前保存的路径或默认导航到 dashboard
                    navigate('/dashboard');
                }, 0);
            }
        } catch (error: any) {
            setState(prev => ({
                ...prev,
                loading: false,
                error: error.message || "登录失败，请检查用户名和密码"
            }));

            toast({
                variant: "destructive",
                title: "登录失败",
                description: error.message || "请检查用户名和密码",
            });
        }
    };

    // 登出方法
    const logout = async () => {
        setState(prev => ({ ...prev, loading: true }));

        try {
            await AuthApi.logout();
        } catch (error) {
            console.error("登出时发生错误", error);
        } finally {
            clearToken();
            // 如果没有记住我，则清除记住我状态
            if (localStorage.getItem(REMEMBER_ME_KEY) !== "true") {
                localStorage.removeItem(REMEMBER_ME_KEY);
            }

            setState({
                isAuthenticated: false,
                user: null,
                token: null,
                loading: false,
                error: null,
            });

            // 同样使用 setTimeout 延迟导航
            setTimeout(() => {
                navigate('/login');
            }, 0);
        }
    };

    // 检查认证状态
    const checkAuth = async () => {
        if (!state.token) {
            setState(prev => ({ ...prev, loading: false, isAuthenticated: false }));
            return false;
        }

        setState(prev => ({ ...prev, loading: true }));

        try {
            const response = await AuthApi.getUserInfo();
            if (response.data) {
                setState({
                    isAuthenticated: true,
                    user: response.data,
                    token: state.token,
                    loading: false,
                    error: null,
                });
                return true;
            } else {
                throw new Error("获取用户信息失败");
            }
        } catch (error) {
            clearToken();
            setState({
                isAuthenticated: false,
                user: null,
                token: null,
                loading: false,
                error: "会话已过期，请重新登录",
            });
            return false;
        }
    };

    // 在组件挂载时检查认证状态
    useEffect(() => {
        checkAuth();
    }, []);

    const value = {
        ...state,
        login,
        logout,
        checkAuth,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// 自定义Hook，用于在组件中访问认证上下文
export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}