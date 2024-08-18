"use client"

import { ColumnDef } from "@tanstack/react-table";
import { Department } from "@/types";

export const columns: ColumnDef<Department>[] = [
    {
        accessorKey: "id",
        header: "ID",
        enableSorting: true,
        enableHiding: true,
    },
    {
        accessorKey: "name",
        header: "名称",
        enableSorting: true,
        enableHiding: true,
    },
    {
        accessorKey: "parentId",
        header: "父部门ID",
        enableSorting: true,
        enableHiding: true,
    },
    {
        accessorKey: "remark",
        header: "备注",
        enableSorting: true,
        enableHiding: true,
    },
    {
        accessorKey: "children",
        header: "子部门",
        enableSorting: false,
        enableHiding: true,
        cell: ({ row }) => {
            const department = row.original;
            return (
                <div className="flex items-center">
                    <span>{department.children?.length || 0}</span>
                </div>
            )
        }
    }
]