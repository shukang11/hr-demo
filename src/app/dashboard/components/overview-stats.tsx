'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useEmployeeOverview } from "@/lib/api/dashboard"
import { Progress } from "@/components/ui/progress"

interface OverviewStatsProps {
  companyId: number
}

export function OverviewStats({ companyId }: OverviewStatsProps) {
  const { data } = useEmployeeOverview(companyId)

  if (!data) {
    return null
  }

  const { 
    totalEmployees,
    departmentDistribution,
    genderDistribution,
    ageDistribution,
  } = data

  // 计算性别分布的百分比
  const total = genderDistribution.male + genderDistribution.female + genderDistribution.unknown
  const malePercent = Math.round((genderDistribution.male / total) * 100)
  const femalePercent = Math.round((genderDistribution.female / total) * 100)
  const unknownPercent = Math.round((genderDistribution.unknown / total) * 100)

  return (
    <div className="grid gap-4 grid-cols-1 lg:grid-cols-2">
      {/* 总人数 */}
      <Card className="col-span-1">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">员工总数</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalEmployees}</div>
        </CardContent>
      </Card>

      {/* 性别分布 */}
      <Card className="col-span-1">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">性别分布</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <div>男</div>
            <div className="text-muted-foreground">{malePercent}%</div>
          </div>
          <Progress value={malePercent} className="h-1" />
          <div className="flex items-center justify-between text-xs">
            <div>女</div>
            <div className="text-muted-foreground">{femalePercent}%</div>
          </div>
          <Progress value={femalePercent} className="h-1" />
          <div className="flex items-center justify-between text-xs">
            <div>未知</div>
            <div className="text-muted-foreground">{unknownPercent}%</div>
          </div>
          <Progress value={unknownPercent} className="h-1" />
        </CardContent>
      </Card>

      {/* 部门分布 */}
      <Card className="col-span-1">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">部门分布</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {departmentDistribution.map(({ department, count }) => {
              const percent = Math.round((count / totalEmployees) * 100)
              return (
                <div key={department} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <div>{department}</div>
                    <div className="text-muted-foreground">{count}人 ({percent}%)</div>
                  </div>
                  <Progress value={percent} className="h-1" />
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* 年龄分布 */}
      <Card className="col-span-1">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">年龄分布</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {ageDistribution.map(({ range, count }) => {
              const percent = Math.round((count / totalEmployees) * 100)
              return (
                <div key={range} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <div>{range}</div>
                    <div className="text-muted-foreground">{count}人 ({percent}%)</div>
                  </div>
                  <Progress value={percent} className="h-1" />
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 