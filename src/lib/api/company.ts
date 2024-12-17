import { PageParams, PageResult } from "@/lib/types"
import { serverAPI, ApiResponse } from "./client"

export interface Company {
  id: number
  name: string
  extra_value?: any
  extra_schema_id?: number
  created_at: string
  updated_at: string
}

export interface InsertCompany {
  id?: number
  name: string
  extra_value?: any
  extra_schema_id?: number
}

const API_PREFIX = "company"

export async function createOrUpdateCompany(data: InsertCompany): Promise<Company> {
  const response = await serverAPI.post(`${API_PREFIX}/create`, {
    json: data
  }).json<ApiResponse<Company>>()
  return response.data
}

export async function getCompanyList(params: PageParams): Promise<PageResult<Company>> {
  console.log('Fetching company list with params:', params);
  const response = await serverAPI.get(`${API_PREFIX}/list`, {
    searchParams: {
      page: params.page.toString(),
      limit: params.limit.toString(),
    }
  }).json<ApiResponse<PageResult<Company>>>();
  console.log('Company list response:', response);
  if (!response.data) {
    throw new Error('No data returned from server');
  }
  return response.data;
}

export async function searchCompanies(name: string, params: PageParams): Promise<PageResult<Company>> {
  const response = await serverAPI.get(`${API_PREFIX}/search`, {
    searchParams: {
      name,
      page: params.page.toString(),
      limit: params.limit.toString(),
    }
  }).json<ApiResponse<PageResult<Company>>>()
  return response.data
}

export async function getCompanyById(id: number): Promise<Company | null> {
  const response = await serverAPI.get(`${API_PREFIX}/${id}`).json<ApiResponse<Company | null>>()
  return response.data
}

export async function deleteCompany(id: number): Promise<void> {
  await serverAPI.delete(`${API_PREFIX}/${id}`).json<ApiResponse<void>>()
} 