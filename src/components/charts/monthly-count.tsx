"use client";

import { cn } from "@/lib/utils";
import { Calendar } from "lucide-react";

interface MonthlyCountProps {
    count: number;
    label: string;
    className?: string;
}

export function MonthlyCount({ count, label, className }: MonthlyCountProps) {
    return (
        <div className={cn("flex items-center", className)}>
            <div className="flex items-center gap-4">
                <div className="p-2 bg-primary/10 rounded-full">
                    <Calendar className="h-10 w-10 text-primary" />
                </div>
                <div>
                    <p className="text-sm font-medium text-muted-foreground">
                        月度{label}
                    </p>
                    <h2 className="text-3xl font-bold tracking-tight">
                        {count}
                    </h2>
                </div>
            </div>
        </div>
    );
}
