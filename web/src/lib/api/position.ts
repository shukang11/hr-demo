import { PageParams, PageResult } from "@/lib/types"
import { serverAPI, ApiResponse } from "./client"
import useSWR from 'swr'

export interface Position {
  id: number
  name: string
  company_id: number
  remark: string | null
  created_at?: string | null
  updated_at?: string | null
}

export interface InsertPosition {
  id?: number
  name: string
  company_id: number
  remark?: string | null
}

const API_PREFIX = "position"

/**
 * 创建或更新职位
 * @param data 职位数据
 */
export async function createOrUpdatePosition(data: InsertPosition): Promise<Position> {
  const response = await serverAPI.post(`${API_PREFIX}/create`, {
    json: data
  }).json<ApiResponse<Position>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取职位列表
 * @param companyId 公司ID
 * @param params 分页参数
 */
export async function getPositionList(
  companyId: number,
  params: PageParams
): Promise<PageResult<Position>> {
  const response = await serverAPI.get(`${API_PREFIX}/list/${companyId}`, {
    searchParams: {
      page: params.page.toString(),
      limit: params.limit.toString(),
    }
  }).json<ApiResponse<PageResult<Position>>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 搜索职位
 * @param companyId 公司ID
 * @param name 搜索关键词
 * @param params 分页参数
 */
export async function searchPositions(
  companyId: number,
  name: string,
  params: PageParams
): Promise<PageResult<Position>> {
  const response = await serverAPI.get(`${API_PREFIX}/search/${companyId}`, {
    searchParams: {
      name,
      page: params.page.toString(),
      limit: params.limit.toString(),
    }
  }).json<ApiResponse<PageResult<Position>>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取职位详情
 * @param id 职位ID
 */
export async function getPositionById(id: number): Promise<Position | null> {
  const response = await serverAPI.get(`${API_PREFIX}/get/${id}`).json<ApiResponse<Position | null>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 删除职位
 * @param id 职位ID
 */
export async function deletePosition(id: number): Promise<void> {
  await serverAPI.post(`${API_PREFIX}/delete/${id}`).json<ApiResponse<void>>();
}

/**
 * 使用 SWR 获取职位列表
 * @param companyId 公司ID
 * @param params 分页参数
 */
export function usePositions(companyId: number | undefined, params: PageParams) {
  return useSWR(
    companyId ? ['positions', companyId, params] : null,
    async () => {
      if (!companyId) return null
      return await getPositionList(companyId, params)
    }
  )
}

/**
 * 使用 SWR 搜索职位
 * @param companyId 公司ID
 * @param keyword 搜索关键词
 * @param params 分页参数
 */
export function usePositionSearch(companyId: number | undefined, keyword: string, params: PageParams) {
  return useSWR(
    companyId && keyword ? ['positions', 'search', companyId, keyword, params] : null,
    async () => {
      if (!companyId) return null
      return await searchPositions(companyId, keyword, params)
    }
  )
}

/**
 * 使用 SWR 获取职位详情
 * @param id 职位ID
 */
export function usePosition(id: number | undefined) {
  return useSWR(
    id ? ['position', id] : null,
    async () => {
      if (!id) return null
      return await getPositionById(id)
    }
  )
} 