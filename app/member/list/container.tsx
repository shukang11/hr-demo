'use client';

import { DataTable } from './data-table';
import React from 'react';
import useSWR from 'swr';
import { columns } from './columns';

// interface ContainerProps { }

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function Container() {
    const { data, error } = useSWR('/data/members.json', fetcher); // 更新路径

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