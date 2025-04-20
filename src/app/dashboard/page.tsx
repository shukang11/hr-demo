'use client'

import { useCompanyStore } from "@/hooks/use-company-store"
import { useEmployeeOverview, useRecruitmentStats, useOrganizationStats } from "@/lib/api/dashboard"
import { OverviewStats } from "./components/overview-stats"
import { RecruitmentStats } from "./components/recruitment-stats"
import { OrganizationStats } from "./components/organization-stats"
import { BirthdayStats } from "./components/birthday-stats"

function LoadingSkeleton() {
  return (
    <div className="space-y-8">
      <div className="h-[300px] rounded-lg bg-muted animate-pulse" />
      <div className="h-[300px] rounded-lg bg-muted animate-pulse" />
      <div className="h-[300px] rounded-lg bg-muted animate-pulse" />
    </div>
  )
}

function EmployeeOverviewSection({ companyId }: { companyId: number }) {
  const { data, error } = useEmployeeOverview(companyId)

  if (error) return <div>加载人员概览数据失败</div>
  if (!data) return <LoadingSkeleton />

  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight mb-4">人员概览</h2>
      <OverviewStats companyId={companyId} />
    </div>
  )
}

function RecruitmentStatsSection({ companyId }: { companyId: number }) {
  const { data, error } = useRecruitmentStats(companyId)

  if (error) return <div>加载招聘概况数据失败</div>
  if (!data) return <LoadingSkeleton />

  const { candidateStatusDistribution, monthlyInterviews, conversionRate } = data

  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight mb-4">招聘概况</h2>
      <RecruitmentStats
        candidateStatusDistribution={candidateStatusDistribution}
        monthlyInterviews={monthlyInterviews}
        conversionRate={conversionRate}
      />
    </div>
  )
}

function OrganizationStatsSection({ companyId }: { companyId: number }) {
  const { data, error } = useOrganizationStats(companyId)

  if (error) return <div>加载组织发展数据失败</div>
  if (!data) return <LoadingSkeleton />

  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight mb-4">组织发展</h2>
      <OrganizationStats {...data} />
    </div>
  )
}

function BirthdaySection({ companyId }: { companyId: number }) {
  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight mb-4">生日提醒</h2>
      <BirthdayStats companyId={companyId} />
    </div>
  )
}

export default function DashboardPage() {
  const { currentCompany } = useCompanyStore()

  if (!currentCompany) {
    return <div>请先选择公司</div>
  }

  return (
    <div className="space-y-8 p-8">
      <EmployeeOverviewSection companyId={currentCompany.id} />
      <RecruitmentStatsSection companyId={currentCompany.id} />
      <OrganizationStatsSection companyId={currentCompany.id} />
      <BirthdaySection companyId={currentCompany.id} />
    </div>
  )
}
