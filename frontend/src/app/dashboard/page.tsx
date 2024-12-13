import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function DashboardPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "仪表盘", href: "/dashboard" },
        { label: "概览" },
      ]}
    >
      <div className="flex w-full flex-col space-y-6">
        {/* 统计卡片 */}
        <div className="grid w-full grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">总员工数</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,234</div>
              <p className="text-xs text-muted-foreground">
                较上月增长 +2.1%
              </p>
            </CardContent>
          </Card>
          {/* 其他统计卡片 */}
        </div>

        {/* 图表区域 */}
        <div className="grid w-full grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Card className="lg:col-span-4">
            <CardHeader>
              <CardTitle>员工增长趋势</CardTitle>
            </CardHeader>
            <CardContent>
              {/* 这里放置折线图 */}
              <div className="h-[300px]" />
            </CardContent>
          </Card>
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>部门分布</CardTitle>
            </CardHeader>
            <CardContent>
              {/* 这里放置饼图 */}
              <div className="h-[300px]" />
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
