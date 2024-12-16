import ky from 'ky';
import MD5 from 'crypto-js/md5';

// API基础配置
const API_BASE_URL = 'http://localhost:5000/';

// API响应接口
interface ApiResponse<T = any> {
  code: number;
  data: T;
  message: string;
}

// 处理API错误
class ApiError extends Error {
  constructor(public code: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

// 创建 ky 实例
const serverAPI = ky.create({
  prefixUrl: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  hooks: {
    beforeError: [
      async error => {
        const { response } = error;
        if (response && response.body) {
          const body = await response.json() as ApiResponse<unknown>;
          throw new ApiError(response.status, body.message || '请求失败');
        }
        throw new ApiError(500, '网络请求错误');
      }
    ]
  },
  retry: 0
});

// API接口类
export class Api {
  // 用户注册
  static async register(username: string, password: string) {
    const hashedPassword = MD5(password).toString();
    return serverAPI.post('api/auth/register', {
      json: { username, password: hashedPassword }
    }).json<ApiResponse<{ message: string }>>();
  }

  // 用户登录
  static async login(username: string, password: string) {
    const hashedPassword = MD5(password).toString();
    return serverAPI.post('api/auth/login', {
      json: { username, password: hashedPassword }
    }).json<ApiResponse<{ token: string }>>();
  }

  // 获取用户信息
  static async getUserInfo() {
    return serverAPI.get('user/info').json<ApiResponse<{ user: any }>>();
  }
}

export default Api;
export {serverAPI};