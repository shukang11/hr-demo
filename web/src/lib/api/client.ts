import ky from "ky";

// API基础配置
const API_BASE_URL = "http://localhost:5001/api/"; // 调整为后端实际运行的端口 5001
const TOKEN_KEY = "hr_auth_token";

// API响应接口
export interface ApiResponse<T = any> {
  data?: T;
  context: {
    code: number;
    message?: string;
    server_at: string;
  };
}

// 处理API错误
export class ApiError extends Error {
  constructor(public code: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

// 获取存储的 token
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

// 保存 token 到本地存储
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

// 清除 token
export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// 创建 ky 实例
export const serverAPI = ky.create({
  prefixUrl: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  hooks: {
    beforeRequest: [
      (request) => {
        // 添加认证令牌到请求头
        const token = getToken();
        console.log(`接口: ${request.url} 添加认证信息: ${token}`);
        if (token) {
          request.headers.set("Authorization", `Bearer ${token}`);
        }

        const url = request.url;
        const method = request.method;
        const body = request.body
          ? request.body instanceof FormData
            ? Object.fromEntries(request.body.entries())
            : request.body
          : undefined;
        const searchParams = Object.fromEntries(
          new URL(url).searchParams.entries()
        );

        console.log("API请求:", {
          url,
          method,
          body: JSON.stringify(body, null, 2),
          searchParams,
          headers: Object.fromEntries(request.headers.entries()),
        });
      },
    ],
    afterResponse: [
      // async (_request, _options, response) => {
      //   try {
      //     const clonedResponse = response.clone();
      //     const responseData = await clonedResponse.json();
      //     console.log("API URL: ", _request.url);
      //     console.log('API响应:', {
      //       status: response.status,
      //       data: responseData
      //     });
      //   } catch (error) {
      //     console.error('解析响应数据失败:', error);
      //   }
      // }
    ],
    beforeError: [
      async (error) => {
        const { response } = error;
        if (response && response.body) {
          const body = (await response.json()) as ApiResponse<unknown>;

          // 如果是401未授权错误，清除本地token
          if (response.status === 401) {
            clearToken();
            // 如果当前不在登录页，可以重定向到登录页
            if (!window.location.href.includes("/login")) {
              window.location.href = "/#/login";
            }
          }

          throw new ApiError(
            response.status,
            body.context.message || "请求失败"
          );
        }
        throw new ApiError(500, "网络请求错误");
      },
    ],
  },
  retry: 0,
});
