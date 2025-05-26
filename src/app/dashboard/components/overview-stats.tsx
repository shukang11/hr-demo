'use client'

import { useEmployeeOverview } from "@/lib/api/dashboard"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts'

interface EmployeeOverviewData {
  totalEmployees: number
  departmentDistribution: Array<{ department: string, count: number }>
  genderDistribution: { male: number, female: number, unknown: number }
  ageDistribution: Array<{ range: string, count: number }>
}

interface OverviewStatsProps {
  companyId?: number
  data?: EmployeeOverviewData
  compact?: boolean
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#4CAF50', '#FF5722']

export function OverviewStats({ companyId, data, compact = false }: OverviewStatsProps) {
  // 如果提供了直接数据，则使用它，否则通过API获取
  const { data: fetchedData } = useEmployeeOverview(companyId)

  // 使用提供的数据或获取的数据
  const overviewData = data || fetchedData

  if (!overviewData) {
    return null
  }

  const {
    totalEmployees,
    departmentDistribution,
    genderDistribution,
    ageDistribution,
  } = overviewData

  // 计算性别分布的百分比和数据
  const total = genderDistribution.male + genderDistribution.female + genderDistribution.unknown
  const malePercent = Math.round((genderDistribution.male / total) * 100)
  const femalePercent = Math.round((genderDistribution.female / total) * 100)
  const unknownPercent = Math.round((genderDistribution.unknown / total) * 100)

  const genderData = [
    { name: '男性', value: genderDistribution.male },
    { name: '女性', value: genderDistribution.female },
    { name: '未知', value: genderDistribution.unknown }
  ].filter(item => item.value > 0)

  // 紧凑布局类
  const gridClass = compact
    ? "grid gap-3 grid-cols-2 md:grid-cols-4"
    : "grid gap-4 grid-cols-1 lg:grid-cols-2"

  const chartHeight = compact ? 180 : 240

  return (
    <div className={gridClass}>
      {/* 总人数 */}
      <Card className={`${compact ? "col-span-1" : "col-span-1"} overflow-hidden`}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <h3 className="text-sm font-medium">员工总数</h3>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalEmployees}</div>
          <div className="text-xs text-muted-foreground">{new Date().toLocaleDateString()} 更新</div>

          {!compact && (
            <div className="mt-4 text-xs">
              <div className="flex justify-between items-center mb-1">
                <span>同比上月</span>
                <span className="text-green-600">+2.5%</span>
              </div>
              <Progress value={70} className="h-1" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* 性别分布 */}
      <Card className={`${compact ? "col-span-1" : "col-span-1"} overflow-hidden`}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <h3 className="text-sm font-medium">性别分布</h3>
        </CardHeader>
        <CardContent>
          {compact ? (
            <ResponsiveContainer width="100%" height={chartHeight}>
              <PieChart>
                <Pie
                  data={genderData}
                  cx="50%"
                  cy="50%"
                  innerRadius={compact ? "60%" : "50%"}
                  outerRadius={compact ? "80%" : "70%"}
                  fill="#8884d8"
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {genderData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span>男性</span>
                <span>{malePercent}% ({genderDistribution.male}人)</span>
              </div>
              <Progress value={malePercent} className="h-1" />

              <div className="flex justify-between text-xs">
                <span>女性</span>
                <span>{femalePercent}% ({genderDistribution.female}人)</span>
              </div>
              <Progress value={femalePercent} className="h-1" />

              <div className="flex justify-between text-xs">
                <span>未知</span>
                <span>{unknownPercent}% ({genderDistribution.unknown}人)</span>
              </div>
              <Progress value={unknownPercent} className="h-1" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* 部门分布 */}
      <Card className={`${compact ? "col-span-1" : "col-span-1"} overflow-hidden`}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <h3 className="text-sm font-medium">部门分布</h3>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={chartHeight}>
            <PieChart>
              <Pie
                data={departmentDistribution}
                cx="50%"
                cy="50%"
                labelLine={!compact}
                outerRadius={compact ? "80%" : "70%"}
                fill="#8884d8"
                dataKey="count"
                nameKey="department"
                label={compact ? false : ({ department, percent }) =>
                  `${department}: ${(percent * 100).toFixed(0)}%`
                }
              >
                {departmentDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              {!compact && <Legend />}
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* 年龄分布 */}
      <Card className={`${compact ? "col-span-1" : "col-span-1"} overflow-hidden`}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <h3 className="text-sm font-medium">年龄分布</h3>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={chartHeight}>
            <BarChart
              data={ageDistribution}
              layout={compact ? "vertical" : "horizontal"}
              margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
            >
              {compact ? (
                <>
                  <XAxis type="number" hide={compact} />
                  <YAxis dataKey="range" type="category" width={40} />
                </>
              ) : (
                <>
                  <XAxis dataKey="range" />
                  <YAxis />
                </>
              )}
              <Tooltip />
              {!compact && <Legend />}
              <Bar
                dataKey="count"
                name="人数"
                fill="#8884d8"
              >
                {ageDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}