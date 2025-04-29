import { get_sha256 } from "../utils";
import {
  serverAPI,
  ApiResponse,
  setToken,
  clearToken,
  getToken,
} from "./client";

// 认证相关 API
export class AuthApi {
  static async login(username: string, password: string) {
    // 这里可以使用 SHA-256 等算法对密码进行哈希处理
    const password_hashed = await get_sha256(password);
    const response = await serverAPI
      .post("auth/login", {
        json: { username, password_hashed },
      })
      .json<ApiResponse<{ token: string; user: any }>>();

    if (response.data?.token) {
      setToken(response.data.token);
    }

    return response;
  }

  static async logout() {
    try {
      await serverAPI.post("auth/logout").json();
    } finally {
      clearToken();
    }
  }

  static async getUserInfo() {
    return await serverAPI.get("auth/info").json<ApiResponse<any>>();
  }

  static async isAuthenticated(): Promise<boolean> {
    const token = getToken();
    if (!token) return false;

    try {
      await this.getUserInfo();
      return true;
    } catch (error) {
      clearToken();
      return false;
    }
  }
}
