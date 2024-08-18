"use client"

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { MAIN_APP } from "@/lib/routes";
import { Employee } from "@/types";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { FC, useState } from "react";

// 在文件顶部添加接口定义
interface ActionProps {
    account: Employee;
}

const Action: FC<ActionProps> = ({ account }) => {
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

export const columns: ColumnDef<Employee>[] = [
    {
        accessorKey: "name",
        header: ({ column }) => (
            <div className="flex items-center">
                <span>姓名</span>
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({ row }) => {
            const account = row.original;
            return (
                <Label onClick={() => alert(`点击了${account.username}`)}>
                    {account.username}
                </Label>
            )
        },
        enableSorting: true,
        enableHiding: true,
    }, {
        accessorKey: "code",
        enableSorting: true,
        enableHiding: true,
        header: ({ column }) => (
            <div className="flex items-center">
                <span>部门</span>
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({ row }) => {
            const account = row.original;
            const department = account.department;
            return (
                <div className="flex items-center">
                    <span>{department?.name}</span>
                </div>
            )
        }
    },
    {
        accessorKey: "joinDate",
        enableSorting: true,
        enableHiding: true,
        header: ({ column }) => (
            <div className="flex items-center">
                <span>入职时间</span>
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            </div>
        ),
        cell: ({ row }) => {
            const account = row.original;
            const inhire = account.employeeInfo;
            let display = "";
            if (inhire) {
                const joinDate = inhire.hireDate;
                display += new Date(joinDate).toLocaleDateString();
            }
            return (
                <div className="flex items-center">
                    <span>{display}</span>
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
            <Action account={row.original} />
            
        )
    }
]