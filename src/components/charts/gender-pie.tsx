"use client";

import { DashboardStats } from "@/lib/api/dashboard";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { cn } from "@/lib/utils";

interface GenderPieProps {
    data: DashboardStats;
    className?: string;
}

export function GenderPie({ data, className }: GenderPieProps) {
    // 转换数据格式
    const genderData = [
        { name: "男性", value: data.genderDistribution.male },
        { name: "女性", value: data.genderDistribution.female },
    ];

    // 如果有未知性别的数据，也添加进去
    if (data.genderDistribution.unknown > 0) {
        genderData.push({ name: "未知", value: data.genderDistribution.unknown });
    }

    // 如果没有任何性别数据，显示提示信息
    if (genderData.every(item => item.value === 0)) {
        return (
            <div className={cn("h-[200px] flex items-center justify-center", className)}>
                <p className="text-muted-foreground">暂无性别数据</p>
            </div>
        );
    }

    // 设置颜色
    const COLORS = ["#3B82F6", "#EC4899", "#94A3B8"];

    // 自定义Tooltip
    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const total = genderData.reduce((sum, item) => sum + item.value, 0);
            const percent = ((payload[0].value / total) * 100).toFixed(1);

            return (
                <div className="bg-background border rounded shadow-sm p-2 text-sm">
                    <p className="font-medium">{`${payload[0].name}: ${payload[0].value}人`}</p>
                    <p className="text-muted-foreground text-xs">{`占比: ${percent}%`}</p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className={cn("h-[200px] w-full", className)}>
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={genderData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) =>
                            `${name}: ${(percent * 100).toFixed(0)}%`
                        }
                    >
                        {genderData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                            />
                        ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
}
