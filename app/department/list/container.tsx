'use client';

import { DataTable } from '@/components/table/data-table';
import React from 'react';
import useSWR from 'swr';
import { columns } from './columns';
import {  useDepartments } from '@/services/department';

// interface ContainerProps { }


export default function Container() {
    
    
    const { data, error } = useDepartments(); // 更新路径

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