"use client";

import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import { timestampToDateString } from "@/lib/utils";
import { useEmployeePositions } from "@/lib/api/employee";
import { useDepartment } from "@/lib/api/department";
import { usePosition } from "@/lib/api/position";

interface EmployeePositionHistoryProps {
    employeeId: number;
}

export function EmployeePositionHistory({ employeeId }: EmployeePositionHistoryProps) {
    const { toast } = useToast();
    const { data: positions, isLoading, error } = useEmployeePositions(employeeId);

    if (isLoading) {
        return <div className="text-center py-4">加载中...</div>;
    }

    if (error || !positions) {
        return (
            <div className="text-destructive text-center py-4">
                加载职位历史失败
            </div>
        );
    }

    if (positions.length === 0) {
        return <div className="text-muted-foreground text-center py-6">无职位历史记录</div>;
    }

    return (
        <div className="space-y-4">
            {positions.map((position, index) => (
                <PositionItem
                    key={position.id}
                    position={position}
                    isCurrentPosition={index === 0}
                />
            ))}
        </div>
    );
}

interface PositionItemProps {
    position: any;
    isCurrentPosition: boolean;
}

function PositionItem({ position, isCurrentPosition }: PositionItemProps) {
    const { data: department } = useDepartment(position.department_id);
    const { data: positionData } = usePosition(position.position_id);

    return (
        <div className="flex items-center justify-between border-b pb-3 last:border-0">
            <div>
                <div className="font-medium">
                    {department?.name || "未知部门"} - {positionData?.name || "未知职位"}
                </div>
                <div className="text-sm text-muted-foreground">
                    {position.start_date ? timestampToDateString(position.start_date) : "未知"}
                    {position.end_date ? ` 至 ${timestampToDateString(position.end_date)}` : " 至今"}
                </div>
            </div>
            {isCurrentPosition && (
                <div className="bg-primary/10 text-primary text-xs px-2 py-1 rounded-full">
                    当前
                </div>
            )}
        </div>
    );
}
