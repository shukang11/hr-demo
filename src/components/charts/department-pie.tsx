"use client";

import { DashboardStats } from "@/lib/api/dashboard";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { cn } from "@/lib/utils";

interface DepartmentPieProps {
    data: DashboardStats;
    className?: string;
}

// 生成漂亮的颜色数组
const COLORS = [
    "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE",
    "#818CF8", "#6366F1", "#4F46E5", "#7C3AED", "#8B5CF6",
    "#A78BFA", "#C4B5FD", "#EA580C", "#F97316", "#FB923C"
];

export function DepartmentPie({ data, className }: DepartmentPieProps) {
    // 获取前5个部门，其余归入"其他"
    let departmentData = [...data.departmentDistribution];

    // 按数量排序
    departmentData.sort((a, b) => b.count - a.count);

    // 如果超过5个部门，将剩余部门合并为"其他"
    if (departmentData.length > 5) {
        const top5 = departmentData.slice(0, 5);
        const others = departmentData.slice(5);
        const othersSum = others.reduce((sum, dept) => sum + dept.count, 0);

        if (othersSum > 0) {
            top5.push({
                department: "其他",
                count: othersSum,
            });
        }

        departmentData = top5;
    }

    // 如果没有数据，显示提示信息
    if (departmentData.length === 0) {
        return (
            <div className={cn("h-[200px] flex items-center justify-center", className)}>
                <p className="text-muted-foreground">暂无部门数据</p>
            </div>
        );
    }

    // 自定义Tooltip显示部门名称和人数
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
                        data={departmentData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                        nameKey="department"
                        label={({ name, percent }) =>
                            `${name}: ${(percent * 100).toFixed(0)}%`
                        }
                    >
                        {departmentData.map((entry, index) => (
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
