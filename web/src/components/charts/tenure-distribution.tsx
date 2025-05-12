"use client";

import { DashboardStats } from "@/lib/api/dashboard";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

interface TenureDistributionProps {
    data: DashboardStats;
    className?: string;
}

export function TenureDistribution({ data, className }: TenureDistributionProps) {
    const tenureData = data.tenureDistribution;

    if (!tenureData || tenureData.length === 0) {
        return (
            <div className={cn("h-[200px] flex items-center justify-center", className)}>
                <p className="text-muted-foreground">暂无任职时长数据</p>
            </div>
        );
    }

    // 自定义Tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-background border rounded shadow-sm p-2 text-sm">
                    <p className="font-medium">{`${label}`}</p>
                    <p className="text-muted-foreground">{`员工数: ${payload[0].value}人`}</p>
                </div>
            );
        }
        return null;
    };

    // 格式化数据并排序
    const chartData = [...tenureData];
    const rangeOrder = ["<1年", "1-3年", "3-5年", "5-10年", ">10年"];
    chartData.sort((a, b) => {
        return rangeOrder.indexOf(a.range) - rangeOrder.indexOf(b.range);
    });

    return (
        <div className={cn("h-[200px] w-full", className)}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={chartData}
                    margin={{
                        top: 10,
                        right: 10,
                        left: 0,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="range" fontSize={12} tickMargin={5} />
                    <YAxis fontSize={12} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#10B981" radius={[4, 4, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
