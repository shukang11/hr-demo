'use client'

import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card"
import {
    ResponsiveContainer, LineChart, Line, BarChart, Bar,
    PieChart, Pie, Cell, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#4CAF50', '#FF5722']

export interface OrganizationStatsType {
    employeeGrowthTrend: Array<{
        month: string
        count: number
    }>
    departmentGrowthTrend: Array<{
        department: string
        trend: Array<{
            month: string
            count: number
        }>
    }>
    positionDistribution: Array<{
        position: string
        count: number
    }>
    tenureDistribution: Array<{
        range: string
        count: number
    }>
}

interface OrganizationStatsProps extends OrganizationStatsType {
    compact?: boolean
}

export function OrganizationStats({
    employeeGrowthTrend,
    departmentGrowthTrend,
    positionDistribution,
    tenureDistribution,
    compact = false
}: OrganizationStatsProps) {
    // 处理职位分布数据
    const pieData = positionDistribution.map(item => ({
        name: item.position,
        value: item.count
    }))

    // 为部门趋势数据创建数据结构
    const formattedDepartmentData = () => {
        // 找出所有月份
        const allMonths = new Set<string>()
        departmentGrowthTrend.forEach(dept => {
            dept.trend.forEach(t => {
                allMonths.add(t.month)
            })
        })

        // 将月份排序
        const sortedMonths = Array.from(allMonths).sort()

        // 创建数据结构
        return sortedMonths.map(month => {
            const monthData: { [key: string]: any } = { month }
            departmentGrowthTrend.forEach(dept => {
                const monthTrend = dept.trend.find(t => t.month === month)
                monthData[dept.department] = monthTrend ? monthTrend.count : 0
            })
            return monthData
        })
    }

    // 紧凑模式下使用2x2网格，提高信息密度
    const gridClass = compact
        ? "grid gap-2 grid-cols-2"
        : "grid gap-4 md:grid-cols-2"

    // 降低图表高度以展示更多信息
    const chartHeight = compact ? 150 : 300

    return (
        <div className={gridClass}>
            {/* 员工增长趋势 */}
            <Card className={compact ? "col-span-2" : "col-span-1"}>
                <CardHeader className="p-2 pb-0">
                    <CardTitle className="text-sm font-medium">员工增长趋势</CardTitle>
                </CardHeader>
                <CardContent className="p-1">
                    <div style={{ height: chartHeight + 'px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={employeeGrowthTrend}>
                                <defs>
                                    <linearGradient id="colorEmployee" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#0088FE" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#0088FE" stopOpacity={0.1} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f5" />
                                <XAxis
                                    dataKey="month"
                                    tick={{ fontSize: compact ? 10 : 12 }}
                                    height={20}
                                    tickMargin={5}
                                />
                                <YAxis
                                    tick={{ fontSize: compact ? 10 : 12 }}
                                    width={25}
                                />
                                <Tooltip formatter={(value) => [`${value} 人`, '员工数量']} />
                                <Legend
                                    wrapperStyle={{ fontSize: compact ? '10px' : '12px' }}
                                    iconSize={8}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="count"
                                    name="员工数量"
                                    stroke="#0088FE"
                                    fillOpacity={1}
                                    fill="url(#colorEmployee)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>

            {/* 部门人员变化趋势 */}
            <Card className={compact ? "col-span-2" : "col-span-1"}>
                <CardHeader className="p-2 pb-0">
                    <CardTitle className="text-sm font-medium">部门人员变化趋势</CardTitle>
                </CardHeader>
                <CardContent className="p-1">
                    <div style={{ height: chartHeight + 'px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={formattedDepartmentData()}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f5" />
                                <XAxis
                                    dataKey="month"
                                    tick={{ fontSize: compact ? 10 : 12 }}
                                    height={20}
                                    tickMargin={5}
                                />
                                <YAxis
                                    tick={{ fontSize: compact ? 10 : 12 }}
                                    width={25}
                                />
                                <Tooltip
                                    contentStyle={{ fontSize: compact ? '10px' : '12px' }}
                                    itemStyle={{ padding: compact ? '1px' : '3px' }}
                                />
                                <Legend
                                    layout={compact ? "horizontal" : "vertical"}
                                    align={compact ? "center" : "right"}
                                    verticalAlign={compact ? "bottom" : "middle"}
                                    wrapperStyle={{ fontSize: compact ? '10px' : '12px', paddingTop: 0 }}
                                    iconSize={8}
                                />
                                {departmentGrowthTrend.map((dept, index) => (
                                    <Bar
                                        key={dept.department}
                                        dataKey={dept.department}
                                        stackId="a"
                                        fill={COLORS[index % COLORS.length]}
                                        barSize={compact ? 10 : 20}
                                    />
                                ))}
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>

            {/* 职位分布 */}
            <Card className="col-span-1">
                <CardHeader className="p-2 pb-0">
                    <CardTitle className="text-sm font-medium">职位分布</CardTitle>
                </CardHeader>
                <CardContent className="p-1">
                    <div style={{ height: chartHeight + 'px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={compact ? "55%" : "45%"}
                                    outerRadius={compact ? "75%" : "65%"}
                                    fill="#8884d8"
                                    paddingAngle={2}
                                    dataKey="value"
                                    nameKey="name"
                                    labelLine={!compact}
                                    label={({ name, percent }) =>
                                        compact ? '' : `${name}: ${(percent * 100).toFixed(0)}%`
                                    }
                                >
                                    {pieData.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value, name) => [`${value} 人 (${((value as number) / pieData.reduce((sum, item) => sum + item.value, 0) * 100).toFixed(1)}%)`, name]} />
                                <Legend
                                    layout={compact ? "horizontal" : "vertical"}
                                    verticalAlign={compact ? "bottom" : "middle"}
                                    align={compact ? "center" : "right"}
                                    iconSize={8}
                                    wrapperStyle={{ fontSize: compact ? '10px' : '12px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>

            {/* 入职时长分布 */}
            <Card className="col-span-1">
                <CardHeader className="p-2 pb-0">
                    <CardTitle className="text-sm font-medium">入职时长分布</CardTitle>
                </CardHeader>
                <CardContent className="p-1">
                    <div style={{ height: chartHeight + 'px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={tenureDistribution}
                                layout="vertical"
                                margin={{ top: 5, right: 15, left: compact ? 60 : 80, bottom: 5 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f5" horizontal={!compact} />
                                <YAxis
                                    dataKey="range"
                                    type="category"
                                    width={compact ? 55 : 70}
                                    tick={{ fontSize: compact ? 10 : 12 }}
                                />
                                <XAxis
                                    type="number"
                                    tick={{ fontSize: compact ? 10 : 12 }}
                                />
                                <Tooltip
                                    formatter={(value) => [`${value} 人`, '员工数量']}
                                    contentStyle={{ fontSize: compact ? '10px' : '12px' }}
                                />
                                <Bar
                                    dataKey="count"
                                    name="员工数量"
                                    fill="#8884d8"
                                    barSize={compact ? 10 : 20}
                                >
                                    {tenureDistribution.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
