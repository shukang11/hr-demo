export interface PageParams {
  page: number;
  limit: number;
}

export interface PageResult<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// 用户信息接口
export interface User {
  id: number;
  username: string;
  email: string;
  gender: number; // 0-未知, 1-男, 2-女
  phone: string | null;
}

// 登录请求接口
export interface LoginRequest {
  username?: string;
  email?: string;
  password_hashed: string;
}

// 登录响应接口
export interface LoginResponse {
  token: string;
  user: User;
}

// 认证上下文状态接口
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}
