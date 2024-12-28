import { PageParams, PageResult } from "@/lib/types"
import { serverAPI, ApiResponse } from "./client"
import useSWR from 'swr'

export interface CandidateListParams extends PageParams {
  status?: string
  search?: string
}

export interface Candidate {
  id: number
  company_id: number
  name: string
  phone: string
  email?: string | null
  position_id: number
  department_id: number
  interview_date?: number | null
  status: string
  interviewer_id: number
  evaluation?: string | null
  remark?: string | null
  extra_value?: any | null
  extra_schema_id?: number | null
  created_at?: number | null
  updated_at?: number | null
}

export interface InsertCandidate {
  id?: number
  company_id: number
  name: string
  phone?: string | null
  email?: string | null
  position_id: number
  department_id: number
  interview_date?: string | null
  interviewer_id?: number | null
  extra_value?: any | null
  extra_schema_id?: number | null
  remark?: string | null
}

export interface UpdateCandidateStatus {
  status: string
  evaluation?: string | null
  remark?: string | null
}

const API_PREFIX = "candidate"

/**
 * 创建或更新候选人
 * @param data 候选人数据
 */
export async function createOrUpdateCandidate(data: InsertCandidate): Promise<Candidate> {
  let timestamp = null;
  if (data.interview_date) {
    const date = new Date(data.interview_date);
    timestamp = date.getTime();
  }
    
  const payload = {
    ...data,
    interview_date: timestamp,
  };
  console.log(`data: ${JSON.stringify(payload)}`);
  const response = await serverAPI.post(`${API_PREFIX}/insert`, {
    json: payload
  }).json<ApiResponse<Candidate>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 更新候选人状态
 * @param id 候选人ID
 * @param data 状态数据
 */
export async function updateCandidateStatus(id: number, data: UpdateCandidateStatus): Promise<Candidate> {
  const response = await serverAPI.post(`${API_PREFIX}/${id}/status`, {
    json: data
  }).json<ApiResponse<Candidate>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取候选人列表
 * @param companyId 公司ID
 * @param params 分页和筛选参数
 */
export async function getCandidateList(companyId: number, params: CandidateListParams): Promise<PageResult<Candidate>> {
  const searchParams: Record<string, string> = {
    page: params.page.toString(),
    limit: params.limit.toString(),
  }

  if (params.status) {
    searchParams.status = params.status
  }

  if (params.search) {
    searchParams.search = params.search
  }

  const response = await serverAPI.get(`${API_PREFIX}/list/${companyId}`, {
    searchParams
  }).json<ApiResponse<PageResult<Candidate>>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取候选人详情
 * @param id 候选人ID
 */
export async function getCandidateById(id: number): Promise<Candidate | null> {
  const response = await serverAPI.get(`${API_PREFIX}/get/${id}`).json<ApiResponse<Candidate | null>>();
  return response.data || null;
}

/**
 * 删除候选人
 * @param id 候选人ID
 */
export async function deleteCandidate(id: number): Promise<void> {
  await serverAPI.post(`${API_PREFIX}/delete/${id}`).json<ApiResponse<void>>();
}

/**
 * 使用 SWR 获取候选人列表
 * @param companyId 公司ID
 * @param params 分页和筛选参数
 */
export function useCandidateList(companyId: number | undefined, params: CandidateListParams) {
  return useSWR(
    companyId ? ['candidates', 'list', companyId, params] : null,
    async () => {
      if (!companyId) return null;
      return await getCandidateList(companyId, params);
    }
  );
}

/**
 * 使用 SWR 获取候选人详情
 * @param id 候选人ID
 */
export function useCandidate(id: number | undefined) {
  return useSWR(
    id ? ['candidate', id] : null,
    async () => {
      if (!id) return null;
      return await getCandidateById(id);
    }
  );
} 