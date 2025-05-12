"use client";

import { DashboardStats } from "@/lib/api/dashboard";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { cn } from "@/lib/utils";

interface PositionDistributionProps {
    data: DashboardStats;
    className?: string;
}

// 生成漂亮的颜色数组
const COLORS = [
    "#F59E0B", "#FBBF24", "#FCD34D", "#FDE68A", "#FEF3C7",
    "#10B981", "#34D399", "#6EE7B7", "#A7F3D0", "#D1FAE5",
    "#EC4899", "#F472B6", "#FBCFE8", "#F43F5E", "#FB7185"
];

export function PositionDistribution({ data, className }: PositionDistributionProps) {
    // 获取前6个职位，其余归入"其他"
    let positionData = [...data.positionDistribution];

    // 按数量排序
    positionData.sort((a, b) => b.count - a.count);

    // 如果超过6个职位，将剩余职位合并为"其他"
    if (positionData.length > 6) {
        const top6 = positionData.slice(0, 6);
        const others = positionData.slice(6);
        const othersSum = others.reduce((sum, pos) => sum + pos.count, 0);

        if (othersSum > 0) {
            top6.push({
                position: "其他",
                count: othersSum,
            });
        }

        positionData = top6;
    }

    // 如果没有数据，显示提示信息
    if (positionData.length === 0) {
        return (
            <div className={cn("h-[200px] flex items-center justify-center", className)}>
                <p className="text-muted-foreground">暂无职位数据</p>
            </div>
        );
    }

    // 将数据转换为饼图可用格式
    const chartData = positionData.map(item => ({
        name: item.position,
        value: item.count
    }));

    // 自定义Tooltip显示职位名称和人数
    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-background border rounded shadow-sm p-2 text-sm">
                    <p className="font-medium">{`${payload[0].name}: ${payload[0].value}人`}</p>
                    <p className="text-muted-foreground text-xs">{`占比: ${(payload[0].percent * 100).toFixed(1)}%`}</p>
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
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) =>
                            percent > 0.05 ? `${name}: ${(percent * 100).toFixed(0)}%` : ''
                        }
                    >
                        {chartData.map((entry, index) => (
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
