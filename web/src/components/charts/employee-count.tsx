"use client";

import { DashboardStats } from "@/lib/api/dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Users } from "lucide-react";

interface EmployeeCountProps {
    data: DashboardStats;
    className?: string;
}

export function EmployeeCount({ data, className }: EmployeeCountProps) {
    return (
        <div className={cn("flex items-center", className)}>
            <div className="flex items-center gap-4">
                <div className="p-2 bg-primary/10 rounded-full">
                    <Users className="h-10 w-10 text-primary" />
                </div>
                <div>
                    <p className="text-sm font-medium text-muted-foreground">
                        集团总人数
                    </p>
                    <h2 className="text-3xl font-bold tracking-tight">
                        {data.totalEmployees}
                    </h2>
                </div>
            </div>
        </div>
    );
}
