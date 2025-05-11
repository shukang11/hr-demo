import { PageParams, PageResult } from "@/lib/types";
import { serverAPI, ApiResponse } from "./client";
import useSWR from "swr";

export interface Company {
  id: number;
  name: string;
  parent_id?: number | null;
  description?: string;
  extra_value?: any;
  extra_schema_id?: number;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface SubsidiaryInfo {
  id: number;
  name: string;
}

export interface CompanyDetail extends Company {
  parent_company?: Company;
  subsidiaries: SubsidiaryInfo[];
}

export interface InsertCompany {
  id?: number;
  name: string;
  parent_id?: number | null;
  description?: string;
  extra_value?: any;
  extra_schema_id?: number;
}

const API_PREFIX = "company";

/**
 * 创建或更新公司
 * @param data 公司数据
 */
export async function createOrUpdateCompany(
  data: InsertCompany
): Promise<Company> {
  const response = await serverAPI
    .post(`${API_PREFIX}/insert/`, {
      json: data,
    })
    .json<ApiResponse<Company>>();
  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 获取公司列表
 * @param params 分页参数
 */
export async function getCompanyList(
  params: PageParams
): Promise<PageResult<Company>> {
  console.log("getCompanyList", params);
  const response = await serverAPI
    .get(`${API_PREFIX}/list/`, {
      searchParams: {
        page: params.page.toString(),
        limit: params.limit.toString(),
      },
    })
    .json<ApiResponse<PageResult<Company>>>();
  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 搜索公司
 * @param name 搜索关键词
 * @param params 分页参数
 */
export async function searchCompanies(
  name: string,
  params: PageParams
): Promise<PageResult<Company>> {
  const response = await serverAPI
    .get(`${API_PREFIX}/search/`, {
      searchParams: {
        name,
        page: params.page.toString(),
        limit: params.limit.toString(),
      },
    })
    .json<ApiResponse<PageResult<Company>>>();
  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 获取公司详情
 * @param id 公司ID
 */
export async function getCompanyById(id: number): Promise<Company | null> {
  const response = await serverAPI
    .get(`${API_PREFIX}/${id}`)
    .json<ApiResponse<Company | null>>();
  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 删除公司
 * @param id 公司ID
 */
export async function deleteCompany(id: number): Promise<void> {
  await serverAPI.delete(`${API_PREFIX}/${id}`).json<ApiResponse<void>>();
}

/**
 * 使用 SWR 获取公司列表
 * @param params 分页参数
 */
export function useCompanies(params: PageParams) {
  return useSWR(
    ["companies", params],
    async () => await getCompanyList(params)
  );
}

/**
 * 使用 SWR 搜索公司
 * @param keyword 搜索关键词
 * @param params 分页参数
 */
export function useCompanySearch(
  keyword: string | undefined,
  params: PageParams
) {
  return useSWR(
    keyword ? ["companies", "search", keyword, params] : null,
    async () => {
      if (!keyword) return null;
      return await searchCompanies(keyword, params);
    }
  );
}

/**
 * 获取公司详细信息（包含子公司）
 * @param id 公司ID
 */
export async function getCompanyDetail(
  id: number
): Promise<CompanyDetail | null> {
  const response = await serverAPI
    .get(`${API_PREFIX}/${id}/detail`)
    .json<ApiResponse<CompanyDetail | null>>();
  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 获取子公司列表
 * @param parentId 父公司ID
 */
export async function getSubsidiaries(parentId: number): Promise<Company[]> {
  const response = await serverAPI
    .get(`${API_PREFIX}/${parentId}/subsidiaries`)
    .json<ApiResponse<Company[]>>();
  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 添加子公司
 * @param parentId 父公司ID
 * @param data 子公司数据
 */
export async function addSubsidiary(
  parentId: number,
  data: InsertCompany
): Promise<Company> {
  const response = await serverAPI
    .post(`${API_PREFIX}/${parentId}/subsidiary`, {
      json: data,
    })
    .json<ApiResponse<Company>>();
  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 使用 SWR 获取公司详情
 * @param id 公司ID
 */
export function useCompany(id: number | undefined) {
  return useSWR(id ? ["company", id] : null, async () => {
    if (!id) return null;
    return await getCompanyById(id);
  });
}

/**
 * 使用 SWR 获取公司详细信息（包含子公司）
 * @param id 公司ID
 */
export function useCompanyDetail(id: number | undefined) {
  return useSWR(id ? ["company", "detail", id] : null, async () => {
    if (!id) return null;
    return await getCompanyDetail(id);
  });
}

/**
 * 使用 SWR 获取子公司列表
 * @param parentId 父公司ID
 */
export function useSubsidiaries(parentId: number | undefined) {
  return useSWR(
    parentId ? ["company", "subsidiaries", parentId] : null,
    async () => {
      if (!parentId) return [];
      return await getSubsidiaries(parentId);
    }
  );
}
