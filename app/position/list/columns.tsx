"use client"

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { MAIN_APP } from "@/lib/routes";
import { Employee, Position } from "@/types";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { FC, useState } from "react";

// 在文件顶部添加接口定义
interface ActionProps {
    position: Position;
}

const Action: FC<ActionProps> = ({ position }) => {
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    const openDialog = () => {
        setIsDialogOpen(true);
    };

    const closeDialog = () => {
        setIsDialogOpen(false);
    };

    return (
        <>
            <div onClick={openDialog}>动作</div>
            {isDialogOpen && (
                <div>
                    <p>对话框内容</p>
                    <button onClick={closeDialog}>关闭</button>
                </div>
            )}
        </>
    )
}

export const columns: ColumnDef<Position>[] = [
    {
        accessorKey: "name",
        header: ({ column }) => (
            <div className="flex items-center">
                <span>职位名称</span>
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({ row }) => {
            const position = row.original;
            return (
                <Label onClick={() => alert(`点击了${position.name}`)}>
                    {position.name}
                </Label>
            )
        },
        enableSorting: true,
        enableHiding: true,
    },
    {
        accessorKey: "company_id",
        enableSorting: true,
        enableHiding: true,
        header: ({ column }) => (
            <div className="flex items-center">
                <span>公司ID</span>
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({ row }) => {
            const position = row.original;
            return (
                <div className="flex items-center">
                    <span>{position.company_id}</span>
                </div>
            )
        }
    },
    {
        accessorKey: "remark",
        enableSorting: true,
        enableHiding: true,
        header: ({ column }) => (
            <div className="flex items-center">
                <span>备注</span>
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({ row }) => {
            const position = row.original;
            return (
                <div className="flex items-center">
                    <span>{position.remark}</span>
                </div>
            )
        }
    },
    {
        accessorKey: "action",
        enableSorting: false,
        enableHiding: false,
        header: "操作",
        cell: ({ row }) => (
            <Action position={row.original} />
        )
    }
]