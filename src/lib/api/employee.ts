import { PageParams, PageResult } from "@/lib/types"
import { serverAPI, ApiResponse } from "./client"
import useSWR from 'swr'

export type Gender = 'Male' | 'Female' | 'Unknown'

export interface Employee {
  id: number
  company_id: number
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
  company_id: number
  name: string
  email?: string | null
  phone?: string | null
  birthdate?: string | null
  address?: string | null
  gender: Gender
  extra_value?: any | null
  extra_schema_id?: number | null
}

export interface EmployeePosition {
  id: number
  employee_id: number
  company_id: number
  department_id: number
  position_id: number
  remark?: string | null
  created_at: string
  updated_at: string
}

export interface InsertEmployeePosition {
  id?: number
  employee_id: number
  company_id: number
  department_id: number
  position_id: number
  remark?: string | null
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
      company_id: data.company_id,
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

/**
 * 为员工添加职位
 * @param data 职位关联数据
 */
export async function addEmployeePosition(data: InsertEmployeePosition): Promise<EmployeePosition> {
  const response = await serverAPI.post(`${API_PREFIX}/position/add`, {
    json: {
      id: data.id || null,
      employee_id: data.employee_id,
      company_id: data.company_id,
      department_id: data.department_id,
      position_id: data.position_id,
      remark: data.remark || null
    }
  }).json<ApiResponse<EmployeePosition>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 移除员工职位
 * @param id 职位关联ID
 */
export async function removeEmployeePosition(id: number): Promise<void> {
  await serverAPI.post(`${API_PREFIX}/position/remove/${id}`).json<ApiResponse<void>>();
}

/**
 * 获取员工的职位列表
 * @param employeeId 员工ID
 */
export async function getEmployeePositions(employeeId: number): Promise<EmployeePosition[]> {
  const response = await serverAPI.get(`${API_PREFIX}/position/list/${employeeId}`)
    .json<ApiResponse<EmployeePosition[]>>();
  if (!response.data) throw new Error('No data returned');
  return response.data;
}

/**
 * 使用 SWR 获取员工职位关联
 * @param employeeId 员工ID
 */
export function useEmployeePositions(employeeId: number | undefined) {
  return useSWR(
    employeeId ? ['employee', 'positions', employeeId] : null,
    async () => {
      if (!employeeId) return null;
      return await getEmployeePositions(employeeId);
    }
  );
} 