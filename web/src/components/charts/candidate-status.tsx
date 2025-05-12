"use client";

import { DashboardStats } from "@/lib/api/dashboard";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

interface CandidateStatusProps {
    data: DashboardStats;
    className?: string;
}

// 候选人状态中文映射
const statusMap: Record<string, string> = {
    pending: "待处理",
    contacted: "已联系",
    scheduled: "已安排面试",
    interviewed: "已面试",
    offer_sent: "已发送Offer",
    accepted: "已接受",
    rejected: "已拒绝",
    withdrawn: "已撤回"
};

export function CandidateStatus({ data, className }: CandidateStatusProps) {
    if (!data.candidateStatusDistribution || data.candidateStatusDistribution.length === 0) {
        return (
            <div className={cn("h-[200px] flex items-center justify-center", className)}>
                <p className="text-muted-foreground">暂无候选人数据</p>
            </div>
        );
    }

    // 自定义Tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            const statusKey = label as keyof typeof statusMap;
            const displayName = statusMap[statusKey] || label;

            return (
                <div className="bg-background border rounded shadow-sm p-2 text-sm">
                    <p className="font-medium">{`${displayName}: ${payload[0].value}人`}</p>
                </div>
            );
        }
        return null;
    };

    // 格式化数据，转换状态名称为中文
    const chartData = data.candidateStatusDistribution.map(item => ({
        status: item.status,
        count: item.count,
        displayName: statusMap[item.status] || item.status
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
                    layout="vertical"
                >
                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                    <XAxis type="number" fontSize={12} />
                    <YAxis
                        type="category"
                        dataKey="displayName"
                        fontSize={12}
                        width={80}
                        tickMargin={5}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#8884d8" radius={[0, 4, 4, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
