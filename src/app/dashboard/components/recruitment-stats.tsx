import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

interface RecruitmentStatsProps {
  candidateStatusDistribution: Array<{
    status: string
    count: number
  }>
  monthlyInterviews: number
  conversionRate: number
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8']

export function RecruitmentStats({
  candidateStatusDistribution,
  monthlyInterviews,
  conversionRate,
}: RecruitmentStatsProps) {
  // 计算转化人数
  const convertedCount = Math.round(monthlyInterviews * conversionRate)

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="text-base">本月招聘概况</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">本月面试</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {monthlyInterviews}
              <span className="text-sm font-normal text-muted-foreground ml-1">人</span>
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">转化率</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {(conversionRate * 100).toFixed(1)}
              <span className="text-sm font-normal text-muted-foreground ml-1">%</span>
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">转化人数</p>
            <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {convertedCount}
              <span className="text-sm font-normal text-muted-foreground ml-1">人</span>
            </p>
          </div>
        </div>
        <div className="h-[240px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={candidateStatusDistribution}
                dataKey="count"
                nameKey="status"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {candidateStatusDistribution.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
} 