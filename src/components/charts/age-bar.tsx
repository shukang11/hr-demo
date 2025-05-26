"use client";

import { DashboardStats } from "@/lib/api/dashboard";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

interface AgeBarProps {
    data: DashboardStats;
    className?: string;
}

export function AgeBar({ data, className }: AgeBarProps) {
    // 如果没有年龄数据，显示提示信息
    if (!data.ageDistribution || data.ageDistribution.length === 0) {
        return (
            <div className={cn("h-[200px] flex items-center justify-center", className)}>
                <p className="text-muted-foreground">暂无年龄数据</p>
            </div>
        );
    }

    // 自定义Tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-background border rounded shadow-sm p-2 text-sm">
                    <p className="font-medium">{`${label}: ${payload[0].value}人`}</p>
                </div>
            );
        }
        return null;
    };

    // 将数据转换为合适的格式
    const chartData = data.ageDistribution.map(item => ({
        range: item.range,
        count: item.count
    }));

    return (
        <div className={cn("h-[200px] w-full", className)}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={chartData}
                    margin={{
                        top: 10,
                        right: 10,
                        left: 0,
                        bottom: 0,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="range" fontSize={12} tickMargin={5} />
                    <YAxis fontSize={12} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
