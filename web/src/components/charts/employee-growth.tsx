"use client";

import { DashboardStats } from "@/lib/api/dashboard";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

interface EmployeeGrowthProps {
    data: DashboardStats;
    className?: string;
}

export function EmployeeGrowth({ data, className }: EmployeeGrowthProps) {
    const growthTrend = data.employeeGrowthTrend;

    if (!growthTrend || growthTrend.length === 0) {
        return (
            <div className={cn("h-[200px] flex items-center justify-center", className)}>
                <p className="text-muted-foreground">暂无员工增长数据</p>
            </div>
        );
    }

    // 自定义Tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            // 将 yyyy-MM 格式转换为 yyyy年MM月
            const dateParts = label.split('-');
            const formattedDate = `${dateParts[0]}年${dateParts[1]}月`;

            return (
                <div className="bg-background border rounded shadow-sm p-2 text-sm">
                    <p className="font-medium">{formattedDate}</p>
                    <p className="text-muted-foreground">{`员工数: ${payload[0].value}人`}</p>
                </div>
            );
        }
        return null;
    };

    // 格式化数据，对于x轴 yyyy-MM 格式仅显示 MM月
    const chartData = growthTrend.map(item => {
        const month = item.month.split('-')[1];
        return {
            month: item.month,
            count: item.count,
            displayMonth: `${month}月`
        };
    });

    return (
        <div className={cn("h-[200px] w-full", className)}>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart
                    data={chartData}
                    margin={{
                        top: 10,
                        right: 10,
                        left: 0,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="displayMonth"
                        fontSize={12}
                        tickMargin={5}
                    />
                    <YAxis fontSize={12} />
                    <Tooltip content={<CustomTooltip />} />
                    <Line
                        type="monotone"
                        dataKey="count"
                        stroke="#3B82F6"
                        activeDot={{ r: 8 }}
                        strokeWidth={2}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
