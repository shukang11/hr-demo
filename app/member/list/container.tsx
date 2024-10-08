'use client';

import { DataTable } from './data-table';
import React from 'react';
import { useEmployees } from '@/services/employ';
import { columns } from './columns';

export default function Container() {
    const { data, error } = useEmployees(); // 更新路径

    console.log(data, error);
    if (error) return <div>加载失败{JSON.stringify(error)}</div>;
    if (!data) return <div>加载中...</div>;

    return (
        <>
            <DataTable
                data={data}
                columns={columns} />
        </>
    )
}