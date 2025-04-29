import { ApiResponse, serverAPI } from "./client"
import useSWR from 'swr'

// 基础类型定义
export interface DepartmentDistribution {
  department: string
  count: number
}

export interface GenderDistribution {
  male: number
  female: number
  unknown: number
}

export interface AgeDistribution {
  range: string
  count: number
}

export interface CandidateStatusDistribution {
  status: string
  count: number
}

export interface DepartmentRecruitment {
  department: string
  openPositions: number
}

export interface MonthlyCount {
  month: string
  count: number
}

export interface DepartmentTrend {
  department: string
  trend: Array<MonthlyCount>
}

export interface PositionDistribution {
  position: string
  count: number
}

export interface TenureDistribution {
  range: string
  count: number
}

// 人员概览
export interface EmployeeOverview {
  totalEmployees: number
  departmentDistribution: Array<DepartmentDistribution>
  genderDistribution: GenderDistribution
  ageDistribution: Array<AgeDistribution>
}

// 招聘概况
export interface RecruitmentStats {
  candidateStatusDistribution: Array<CandidateStatusDistribution>
  monthlyInterviews: number
  conversionRate: number
  departmentRecruitmentTop5: Array<DepartmentRecruitment>
}

// 组织发展
export interface OrganizationStats {
  employeeGrowthTrend: Array<MonthlyCount>
  departmentGrowthTrend: Array<DepartmentTrend>
  positionDistribution: Array<PositionDistribution>
  tenureDistribution: Array<TenureDistribution>
}

// 完整看板数据
export interface DashboardStats extends EmployeeOverview, RecruitmentStats, OrganizationStats {}

// 生日员工信息
export interface BirthdayEmployee {
  id: number
  name: string
  department: string
  position: string
  birthdate: number
}

// API 函数
export async function getDashboardStats(companyId: number): Promise<DashboardStats> {
  // 默认获取最近12个月的数据
  const now = new Date()
  const startTime = new Date(now.getFullYear(), now.getMonth() - 11, 1).getTime()
  const endTime = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999).getTime()

  const response = await serverAPI.get(`dashboard/stats/${companyId}`, {
    searchParams: {
      start_time: startTime.toString(),
      end_time: endTime.toString(),
    }
  }).json<ApiResponse<DashboardStats>>()
  if (!response.data) throw new Error('No data returned')
  return response.data
}

export async function getEmployeeOverview(companyId: number): Promise<EmployeeOverview> {
  // 默认获取最近12个月的数据
  const now = new Date()
  const startTime = new Date(now.getFullYear(), now.getMonth() - 11, 1).getTime()
  const endTime = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999).getTime()

  const response = await serverAPI.get(`dashboard/employee-overview/${companyId}`, {
    searchParams: {
      start_time: startTime.toString(),
      end_time: endTime.toString(),
    }
  }).json<ApiResponse<EmployeeOverview>>()
  if (!response.data) throw new Error('No data returned')
  return response.data
}

export async function getRecruitmentStats(companyId: number): Promise<RecruitmentStats> {
  // 默认获取最近12个月的数据
  const now = new Date()
  const startTime = new Date(now.getFullYear(), now.getMonth() - 11, 1).getTime()
  const endTime = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999).getTime()

  const response = await serverAPI.get(`dashboard/recruitment-stats/${companyId}`, {
    searchParams: {
      start_time: startTime.toString(),
      end_time: endTime.toString(),
    }
  }).json<ApiResponse<RecruitmentStats>>()
  if (!response.data) throw new Error('No data returned')
  return response.data
}

export async function getOrganizationStats(companyId: number): Promise<OrganizationStats> {
  // 默认获取最近12个月的数据
  const now = new Date()
  const startTime = new Date(now.getFullYear(), now.getMonth() - 11, 1).getTime()
  const endTime = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999).getTime()

  const response = await serverAPI.get(`dashboard/organization-stats/${companyId}`, {
    searchParams: {
      start_time: startTime.toString(),
      end_time: endTime.toString(),
    }
  }).json<ApiResponse<OrganizationStats>>()
  if (!response.data) throw new Error('No data returned')
  return response.data
}

export async function getBirthdayEmployees(
  companyId: number,
  startTime: number,
  endTime: number
): Promise<BirthdayEmployee[]> {
  const response = await serverAPI
    .get(`dashboard/birthday-employees/${companyId}`, {
      searchParams: {
        start_time: startTime.toString(),
        end_time: endTime.toString(),
      }
    })
    .json<ApiResponse<BirthdayEmployee[]>>()
  if (!response.data) throw new Error('No data returned')
  return response.data
}

// SWR Hooks
export function useDashboardStats(companyId: number | undefined) {
  return useSWR(
    companyId ? ['dashboard', 'stats', companyId] : null,
    async () => {
      if (!companyId) return null
      return await getDashboardStats(companyId)
    }
  )
}

export function useEmployeeOverview(companyId: number | undefined) {
  return useSWR(
    companyId ? ['dashboard', 'employee-overview', companyId] : null,
    async () => {
      if (!companyId) return null
      return await getEmployeeOverview(companyId)
    }
  )
}

export function useRecruitmentStats(companyId: number | undefined) {
  return useSWR(
    companyId ? ['dashboard', 'recruitment-stats', companyId] : null,
    async () => {
      if (!companyId) return null
      return await getRecruitmentStats(companyId)
    }
  )
}

export function useOrganizationStats(companyId: number | undefined) {
  return useSWR(
    companyId ? ['dashboard', 'organization-stats', companyId] : null,
    async () => {
      if (!companyId) return null
      return await getOrganizationStats(companyId)
    }
  )
}

export function useBirthdayEmployees(
  companyId: number | undefined,
  startTime: number | undefined,
  endTime: number | undefined
) {
  return useSWR(
    companyId && startTime && endTime
      ? ['dashboard', 'birthday-employees', companyId, startTime, endTime]
      : null,
    async () => {
      if (!companyId || !startTime || !endTime) return null
      return await getBirthdayEmployees(companyId, startTime, endTime)
    }
  )
} 