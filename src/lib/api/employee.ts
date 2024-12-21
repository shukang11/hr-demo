import { PageParams, PageResult } from "@/lib/types"
import { serverAPI, ApiResponse } from "./client"
import useSWR from 'swr'

export type Gender = 'Male' | 'Female' | 'Unknown'

export interface Employee {
  id: number
  name: string
  email?: string | null
  phone?: string | null
  birthdate?: string | null
  address?: string | null
  gender: Gender
  extra_value?: any | null
  extra_schema_id?: number | null
  created_at: string
  updated_at: string
}

export interface InsertEmployee {
  id?: number
  name: string
  email?: string | null
  phone?: string | null
  birthdate?: string | null
  address?: string | null
  gender: Gender
  extra_value?: any | null
  extra_schema_id?: number | null
  company_id: number
}

const API_PREFIX = "employee"

/**
 * 创建或更新员工
 * @param data 员工数据
 */
export async function createOrUpdateEmployee(data: InsertEmployee): Promise<Employee> {
  const response = await serverAPI.post(`${API_PREFIX}/insert`, {
    json: {
      id: data.id || null,
      name: data.name,
      email: data.email || null,
      phone: data.phone || null,
      birthdate: data.birthdate || null,
      address: data.address || null,
      gender: data.gender,
      extra_value: data.extra_value || null,
      extra_schema_id: data.extra_schema_id || null
    }
  }).json<ApiResponse<Employee>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取员工列表
 * @param companyId 公司ID
 * @param params 分页参数
 */
export async function getEmployeeList(
  companyId: number,
  params: PageParams
): Promise<PageResult<Employee>> {
  const response = await serverAPI.get(`${API_PREFIX}/list/${companyId}`, {
    searchParams: {
      page: params.page.toString(),
      limit: params.limit.toString(),
    }
  }).json<ApiResponse<PageResult<Employee>>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取部门的员工列表
 * @param departmentId 部门ID
 * @param params 分页参数
 */
export async function getEmployeesByDepartment(
  departmentId: number,
  params: PageParams
): Promise<PageResult<Employee>> {
  const response = await serverAPI.get(`${API_PREFIX}/list/department/${departmentId}`, {
    searchParams: {
      page: params.page.toString(),
      limit: params.limit.toString(),
    }
  }).json<ApiResponse<PageResult<Employee>>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 搜索员工
 * @param companyId 公司ID
 * @param name 搜索关键词
 * @param params 分页参数
 */
export async function searchEmployees(
  companyId: number,
  name: string,
  params: PageParams
): Promise<PageResult<Employee>> {
  const response = await serverAPI.get(`${API_PREFIX}/search/${companyId}`, {
    searchParams: {
      name,
      page: params.page.toString(),
      limit: params.limit.toString(),
    }
  }).json<ApiResponse<PageResult<Employee>>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 获取员工详情
 * @param id 员工ID
 */
export async function getEmployeeById(id: number): Promise<Employee | null> {
  const response = await serverAPI.get(`${API_PREFIX}/get/${id}`).json<ApiResponse<Employee | null>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 删除员工
 * @param id 员工ID
 */
export async function deleteEmployee(id: number): Promise<void> {
  await serverAPI.post(`${API_PREFIX}/delete/${id}`).json<ApiResponse<void>>();
}

/**
 * 使用 SWR 获取员工列表
 * @param companyId 公司ID
 * @param params 分页参数
 */
export function useEmployees(companyId: number | undefined, params: PageParams) {
  return useSWR(
    companyId ? ['employees', companyId, params] : null,
    async () => {
      if (!companyId) return null
      return await getEmployeeList(companyId, params)
    }
  )
}

/**
 * 使用 SWR 获取部门的员工列表
 * @param departmentId 部门ID
 * @param params 分页参数
 */
export function useEmployeesByDepartment(departmentId: number | undefined, params: PageParams) {
  return useSWR(
    departmentId ? ['employees', 'department', departmentId, params] : null,
    async () => {
      if (!departmentId) return null
      return await getEmployeesByDepartment(departmentId, params)
    }
  )
}

/**
 * 使用 SWR 搜索员工
 * @param companyId 公司ID
 * @param keyword 搜索关键词
 * @param params 分页参数
 */
export function useEmployeeSearch(companyId: number | undefined, keyword: string, params: PageParams) {
  return useSWR(
    companyId && keyword ? ['employees', 'search', companyId, keyword, params] : null,
    async () => {
      if (!companyId) return null
      return await searchEmployees(companyId, keyword, params)
    }
  )
}

/**
 * 使用 SWR 获取员工详情
 * @param id 员工ID
 */
export function useEmployee(id: number | undefined) {
  return useSWR(
    id ? ['employee', id] : null,
    async () => {
      if (!id) return null
      return await getEmployeeById(id)
    }
  )
} 