'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
    ResponsiveContainer, PieChart, Pie, Cell,
    BarChart, Bar, XAxis, YAxis, Tooltip, Legend
} from 'recharts'

interface RecruitmentStatsProps {
    candidateStatusDistribution: Array<{
        status: string
        count: number
    }>
    monthlyInterviews: number
    conversionRate: number
    compact?: boolean
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#4CAF50', '#FF5722']

export function RecruitmentStats({
    candidateStatusDistribution,
    monthlyInterviews,
    conversionRate,
    compact = false
}: RecruitmentStatsProps) {
    // 计算转化人数
    const convertedCount = Math.round(monthlyInterviews * conversionRate)

    // 计算候选人总数
    const totalCandidates = candidateStatusDistribution.reduce((sum, item) => sum + item.count, 0)

    // 格式化候选人数据为图表数据
    const pieData = candidateStatusDistribution.map(item => ({
        name: item.status,
        value: item.count
    }))

    const statusBarData = candidateStatusDistribution.map(item => ({
        name: item.status,
        count: item.count,
        percentage: (item.count / totalCandidates * 100).toFixed(1)
    }))

    return (
        <div className={compact ? "space-y-1" : ""}>
            {compact ? (
                <>
                    {/* 紧凑视图 - 统计数据以小卡片形式展示 */}
                    <div className="grid grid-cols-6 gap-1">
                        <div className="p-1 border rounded-md">
                            <p className="text-xs text-muted-foreground">本月面试</p>
                            <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                                {monthlyInterviews}人
                            </p>
                        </div>
                        <div className="p-1 border rounded-md">
                            <p className="text-xs text-muted-foreground">转化率</p>
                            <p className="text-lg font-bold text-green-600 dark:text-green-400">
                                {(conversionRate * 100).toFixed(1)}%
                            </p>
                        </div>
                        <div className="p-1 border rounded-md">
                            <p className="text-xs text-muted-foreground">转化人数</p>
                            <p className="text-lg font-bold text-purple-600 dark:text-purple-400">
                                {convertedCount}人
                            </p>
                        </div>
                        <div className="p-1 border rounded-md">
                            <p className="text-xs text-muted-foreground">候选人总数</p>
                            <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
                                {totalCandidates}人
                            </p>
                        </div>
                        <div className="p-1 border rounded-md">
                            <p className="text-xs text-muted-foreground">平均面试时长</p>
                            <p className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                                50分钟
                            </p>
                        </div>
                        <div className="p-1 border rounded-md">
                            <p className="text-xs text-muted-foreground">平均招聘周期</p>
                            <p className="text-lg font-bold text-pink-600 dark:text-pink-400">
                                15天
                            </p>
                        </div>
                    </div>

                    {/* 图表区域 */}
                    <div className="grid grid-cols-2 gap-2 mt-2">
                        <div style={{ height: "150px" }}>
                            <h4 className="text-xs font-medium mb-1">候选人状态分布</h4>
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius="55%"
                                        outerRadius="75%"
                                        fill="#8884d8"
                                        paddingAngle={2}
                                        dataKey="value"
                                        nameKey="name"
                                        label={false}
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value, name) => [`${value} 人 (${((value as number) / totalCandidates * 100).toFixed(1)}%)`, name]} />
                                    <Legend
                                        layout="horizontal"
                                        verticalAlign="bottom"
                                        align="center"
                                        iconSize={8}
                                        wrapperStyle={{ fontSize: '10px' }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>

                        <div style={{ height: "150px" }}>
                            <h4 className="text-xs font-medium mb-1">候选人状态比例</h4>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={statusBarData}
                                    layout="vertical"
                                    margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
                                >
                                    <XAxis type="number" tick={{ fontSize: 10 }} />
                                    <YAxis
                                        type="category"
                                        dataKey="name"
                                        width={60}
                                        tick={{ fontSize: 10 }}
                                    />
                                    <Tooltip formatter={(value) => [`${value}%`, '百分比']} />
                                    <Bar dataKey="percentage" fill="#8884d8" barSize={12}>
                                        {statusBarData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </>
            ) : (
                <>
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">本月招聘概况</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-3 gap-4 mb-6">
                                <div className="space-y-2">
                                    <p className="text-sm text-muted-foreground">本月面试</p>
                                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                        {monthlyInterviews}人
                                    </p>
                                </div>
                                <div className="space-y-2">
                                    <p className="text-sm text-muted-foreground">转化率</p>
                                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                                        {(conversionRate * 100).toFixed(1)}%
                                    </p>
                                </div>
                                <div className="space-y-2">
                                    <p className="text-sm text-muted-foreground">转化人数</p>
                                    <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                                        {convertedCount}人
                                    </p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 gap-4">
                                <div className="h-[300px]">
                                    <h4 className="text-sm font-medium mb-4">候选人状态分布</h4>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={pieData}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius="40%"
                                                outerRadius="60%"
                                                fill="#8884d8"
                                                paddingAngle={2}
                                                dataKey="value"
                                                nameKey="name"
                                                label={({ name, percent }) =>
                                                    `${name}: ${(percent * 100).toFixed(0)}%`
                                                }
                                            >
                                                {pieData.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip formatter={(value) => [`${value}人`, '数量']} />
                                            <Legend />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </>
            )}
        </div>
    )
}
