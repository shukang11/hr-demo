import ky from 'ky';
import MD5 from 'crypto-js/md5';

// API基础配置
const API_BASE_URL = 'http://localhost:5000/';

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
    this.name = 'ApiError';
  }
}

// 创建 ky 实例
export const serverAPI = ky.create({
  prefixUrl: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  hooks: {
    beforeRequest: [
      request => {
        const url = request.url;
        const method = request.method;
        const body = request.body ? 
          (request.body instanceof FormData ? 
            Object.fromEntries(request.body.entries()) : 
            request.body) 
          : undefined;
        const searchParams = Object.fromEntries(new URL(url).searchParams.entries());
        
        console.log('API请求:', {
          url,
          method,
          body: JSON.stringify(body, null, 2),
          searchParams,
          headers: Object.fromEntries(request.headers.entries())
        });
      }
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
      async error => {
        const { response } = error;
        if (response && response.body) {
          const body = await response.json() as ApiResponse<unknown>;
          throw new ApiError(response.status, body.context.message || '请求失败');
        }
        throw new ApiError(500, '网络请求错误');
      }
    ]
  },
  retry: 0
});

// 认证相关 API
export class AuthApi {
  static async register(username: string, password: string) {
    const hashedPassword = MD5(password).toString();
    return serverAPI.post('api/auth/register', {
      json: { username, password: hashedPassword }
    }).json<ApiResponse<{ message: string }>>();
  }

  static async login(username: string, password: string) {
    const hashedPassword = MD5(password).toString();
    return serverAPI.post('api/auth/login', {
      json: { username, password: hashedPassword }
    }).json<ApiResponse<{ token: string }>>();
  }

  static async getUserInfo() {
    return serverAPI.get('user/info').json<ApiResponse<{ user: any }>>();
  }
} 