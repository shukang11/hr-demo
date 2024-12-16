import { PageParams, PageResult } from "@/lib/types"

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

const API_PREFIX = "/api/company"

export async function createOrUpdateCompany(data: InsertCompany): Promise<Company> {
  const response = await fetch(API_PREFIX, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
  const result = await response.json()
  return result.data
}

export async function getCompanyList(params: PageParams): Promise<PageResult<Company>> {
  const searchParams = new URLSearchParams({
    page: params.page.toString(),
    limit: params.limit.toString(),
  })
  const response = await fetch(`${API_PREFIX}?${searchParams}`)
  const result = await response.json()
  return result.data
}

export async function searchCompanies(name: string, params: PageParams): Promise<PageResult<Company>> {
  const searchParams = new URLSearchParams({
    name,
    page: params.page.toString(),
    limit: params.limit.toString(),
  })
  const response = await fetch(`${API_PREFIX}/search?${searchParams}`)
  const result = await response.json()
  return result.data
}

export async function getCompanyById(id: number): Promise<Company | null> {
  const response = await fetch(`${API_PREFIX}/${id}`)
  const result = await response.json()
  return result.data
}

export async function deleteCompany(id: number): Promise<void> {
  await fetch(`${API_PREFIX}/${id}`, {
    method: "DELETE",
  })
} 