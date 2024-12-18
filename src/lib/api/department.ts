import { PageParams, PageResult } from "@/lib/types"
import { serverAPI, ApiResponse } from "./client"

export interface Department {
  id: number
  name: string
  parent_id?: number
  company_id: number
  leader_id?: number
  remark?: string
  created_at: string
  updated_at: string
}

export interface InsertDepartment {
  id?: number
  name: string
  parent_id?: number
  company_id: number
  leader_id?: number
  remark?: string
}

const API_PREFIX = "department"

/**
 * 创建或更新部门
 */
export async function insertDepartment(data: InsertDepartment): Promise<Department> {
  const response = await serverAPI.post(`${API_PREFIX}/insert`, {
    json: data
  }).json<ApiResponse<Department>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取公司的部门列表
 */
export async function getDepartmentList(companyId: number, params: PageParams): Promise<PageResult<Department>> {
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
 */
export async function searchDepartments(companyId: number, name: string, params: PageParams): Promise<PageResult<Department>> {
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
 */
export async function getDepartmentById(id: number): Promise<Department | null> {
  const response = await serverAPI.get(`${API_PREFIX}/get/${id}`).json<ApiResponse<Department | null>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 删除部门
 */
export async function deleteDepartment(id: number): Promise<void> {
  await serverAPI.post(`${API_PREFIX}/delete/${id}`).json<ApiResponse<void>>();
} 