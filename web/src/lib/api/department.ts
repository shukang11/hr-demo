import { PageParams, PageResult } from "@/lib/types"
import { serverAPI, ApiResponse } from "./client"
import useSWR from 'swr'

export interface Department {
  id: number
  name: string
  parent_id?: number | null
  company_id: number
  leader_id?: number | null
  remark?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export interface InsertDepartment {
  id?: number
  name: string
  parent_id?: number | null
  company_id: number
  leader_id?: number | null
  remark?: string | null
}

const API_PREFIX = "department"

/**
 * 创建或更新部门
 * @param data 部门数据
 */
export async function createOrUpdateDepartment(data: InsertDepartment): Promise<Department> {
  const response = await serverAPI.post(`${API_PREFIX}/insert`, {
    json: {
      id: data.id || null,
      name: data.name,
      company_id: data.company_id,
      parent_id: data.parent_id || null,
      leader_id: data.leader_id || null,
      remark: data.remark || null
    }
  }).json<ApiResponse<Department>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取部门列表
 * @param companyId 公司ID
 * @param params 分页参数
 */
export async function getDepartmentList(
  companyId: number,
  params: PageParams
): Promise<PageResult<Department>> {
  const response = await serverAPI.get(`${API_PREFIX}/list/${companyId}`, {
    searchParams: {
      page: params.page.toString(),
      limit: params.limit.toString(),
    }
  }).json<ApiResponse<PageResult<Department>>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 搜索部门
 * @param companyId 公司ID
 * @param name 搜索关键词
 * @param params 分页参数
 */
export async function searchDepartments(
  companyId: number,
  name: string,
  params: PageParams
): Promise<PageResult<Department>> {
  const response = await serverAPI.get(`${API_PREFIX}/search/${companyId}`, {
    searchParams: {
      name,
      page: params.page.toString(),
      limit: params.limit.toString(),
    }
  }).json<ApiResponse<PageResult<Department>>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取部门详情
 * @param id 部门ID
 */
export async function getDepartmentById(id: number): Promise<Department | null> {
  const response = await serverAPI.get(`${API_PREFIX}/get/${id}`).json<ApiResponse<Department | null>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 删除部门
 * @param id 部门ID
 */
export async function deleteDepartment(id: number): Promise<void> {
  await serverAPI.post(`${API_PREFIX}/delete/${id}`).json<ApiResponse<void>>();
}

/**
 * 使用 SWR 获取部门列表
 * @param companyId 公司ID
 * @param params 分页参数
 */
export function useDepartments(companyId: number | undefined, params: PageParams) {
  return useSWR(
    companyId ? ['departments', companyId, params] : null,
    async () => {
      if (!companyId) return null
      return await getDepartmentList(companyId, params)
    }
  )
}

/**
 * 使用 SWR 搜索部门
 * @param companyId 公司ID
 * @param keyword 搜索关键词
 * @param params 分页参数
 */
export function useDepartmentSearch(companyId: number | undefined, keyword: string, params: PageParams) {
  return useSWR(
    companyId && keyword ? ['departments', 'search', companyId, keyword, params] : null,
    async () => {
      if (!companyId) return null
      return await searchDepartments(companyId, keyword, params)
    }
  )
}

/**
 * 使用 SWR 获取部门详情
 * @param id 部门ID
 */
export function useDepartment(id: number | undefined) {
  return useSWR(
    id ? ['department', id] : null,
    async () => {
      if (!id) return null
      return await getDepartmentById(id)
    }
  )
} 