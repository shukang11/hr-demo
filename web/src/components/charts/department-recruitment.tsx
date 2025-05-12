"use client";

import { DashboardStats } from "@/lib/api/dashboard";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

interface DepartmentRecruitmentProps {
    data: DashboardStats;
    className?: string;
}

export function DepartmentRecruitment({ data, className }: DepartmentRecruitmentProps) {
    const departmentRecruitment = data.departmentRecruitmentTop5;

    if (!departmentRecruitment || departmentRecruitment.length === 0) {
        return (
            <div className={cn("h-[200px] flex items-center justify-center", className)}>
                <p className="text-muted-foreground">暂无部门招聘数据</p>
            </div>
        );
    }

    // 自定义Tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-background border rounded shadow-sm p-2 text-sm">
                    <p className="font-medium">{`${label}`}</p>
                    <p className="text-muted-foreground">{`空缺职位: ${payload[0].value}个`}</p>
                </div>
            );
        }
        return null;
    };

    // 格式化数据
    const chartData = departmentRecruitment.map(item => ({
        department: item.department,
        openPositions: item.openPositions
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
                        bottom: 5,
                    }}
                    layout="vertical"
                >
                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                    <XAxis type="number" fontSize={12} />
                    <YAxis
                        type="category"
                        dataKey="department"
                        fontSize={12}
                        width={100}
                        tickMargin={5}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="openPositions" fill="#F59E0B" radius={[0, 4, 4, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
