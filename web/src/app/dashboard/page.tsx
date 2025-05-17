'use client'

import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardDescription } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Download, RefreshCw } from "lucide-react"

// 自定义组件
import { OverviewStats } from "./components/overview-stats"
import { RecruitmentStats } from "./components/recruitment-stats"
import { OrganizationStats } from "./components/organization-stats"
import { BirthdayStats } from "./components/birthday-stats"

// API调用
import { useDashboardStats } from "@/lib/api/dashboard"
import { useCompanyStore } from "@/hooks/use-company-store"

export default function DashboardPage() {
  // 从 Store 获取当前选择的公司
  const { currentCompany } = useCompanyStore();

  // 加载公司整体数据
  const {
    data: dashboardData,
    isLoading,
    error,
    mutate: refetchData
  } = useDashboardStats(currentCompany?.id)

  // 刷新数据
  const handleRefresh = () => {
    try {
      refetchData();
    } catch (error) {
      console.error("刷新数据失败:", error);
    }
  }

  // 导出数据
  const handleExport = () => {
    // 导出功能将在后续版本实现
    alert("导出功能将在后续版本实现");
  }

  // 如果没有选择公司
  if (!currentCompany?.id) {
    return (
      <div className="p-4">
        <h1 className="text-xl font-bold mb-4">公司仪表盘</h1>
        <Card className="mt-4">
          <CardHeader>
            <CardDescription>
              请先在顶部选择一个公司以查看仪表盘数据
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  // 错误处理
  if (error) {
    return (
      <div className="p-4">
        <h1 className="text-xl font-bold mb-4">仪表盘</h1>
        <Card className="mt-4">
          <CardHeader>
            <CardDescription className="text-destructive">
              加载数据时发生错误，请尝试刷新页面或稍后再试
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          {currentCompany.name} - 公司仪表盘
        </h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            刷新数据
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
          >
            <Download className="h-4 w-4 mr-2" />
            导出报告
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="p-4 text-center">数据加载中...</div>
      ) : (
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid grid-cols-4 max-w-[600px]">
            <TabsTrigger value="overview">总览</TabsTrigger>
            <TabsTrigger value="recruitment">招聘情况</TabsTrigger>
            <TabsTrigger value="organization">组织架构</TabsTrigger>
            <TabsTrigger value="birthday">生日提醒</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            {dashboardData && <OverviewStats data={dashboardData} />}
          </TabsContent>

          <TabsContent value="recruitment" className="space-y-4">
            {dashboardData && (
              <RecruitmentStats
                candidateStatusDistribution={dashboardData.candidateStatusDistribution}
                monthlyInterviews={dashboardData.monthlyInterviews}
                conversionRate={dashboardData.conversionRate}
              />
            )}
          </TabsContent>

          <TabsContent value="organization" className="space-y-4">
            {dashboardData && (
              <OrganizationStats
                employeeGrowthTrend={dashboardData.employeeGrowthTrend}
                departmentGrowthTrend={dashboardData.departmentGrowthTrend}
                positionDistribution={dashboardData.positionDistribution}
                tenureDistribution={dashboardData.tenureDistribution}
              />
            )}
          </TabsContent>

          <TabsContent value="birthday" className="space-y-4">
            {currentCompany && (
              <BirthdayStats companyId={currentCompany.id} />
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}