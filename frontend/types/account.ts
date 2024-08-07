export type Role = 0 | 2; // 0 Standard User; 2 Member User

export type RedisUserId = string | null;

export interface UserId {
  userId: string;
}

export enum AccountStatus {
  // 正常
  NORMAL = 0,
  // 不可用
  DISABLE = 1,
}

export interface AccountInfo {
  id: string;
  username?: string;
  email: string;
  phone?: string;

  status: AccountStatus;

  // avatar?: string;
  // platform: string;
  // membershipExpire?: number;
  // accessToken?: string;
}

export interface AccountAndToken {
  account: AccountInfo;
  token: string;
}
