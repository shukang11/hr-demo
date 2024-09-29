'use client';

import { DataTable } from './data-table';
import React, { useState } from 'react';
import { useEmployees } from '@/services/employ';
import { columns } from './columns';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input"; // 引入 shadcn 组件
import Link from "next/link";
import { MEMBER_APP } from "@/lib/routes";

export default function Container() {
    const { data, error } = useEmployees(); // 更新路径
    const [query, setQuery] = useState('');

    const filteredData = data?.filter(employee =>
        employee.username.toLowerCase().includes(query.toLowerCase()) ||
        employee.department?.name.toLowerCase().includes(query.toLowerCase())
    );

    console.log(data, error);
    if (error) return <div>加载失败{JSON.stringify(error)}</div>;
    if (!data) return <div>加载中...</div>;

    return (
        <>
            <div className="flex flex-col">
                <div className="flex justify-end mb-10 space-x-4">
                    <div className="mb-4">
                        <Input
                            type="text"
                            placeholder="搜索员工"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="p-2 border border-gray-300 rounded"
                        />
                    </div>

                    <Link href={MEMBER_APP.insert}>
                        <Button>新增</Button>
                    </Link>
                    <Button>导出</Button>
                </div>
                <DataTable
                    data={filteredData || []}
                    columns={columns}
                />
            </div>


        </>
    )
}