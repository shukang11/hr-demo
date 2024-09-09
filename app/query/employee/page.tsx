'use client';

import React, { useEffect, useState } from 'react';

import { useEmployees } from '@/services/employ';

export default function Page() {
    const { data: employeeList, error } = useEmployees();

    const [retentionData, setRetentionData] = useState<{ total: number, retained: number, left: number }>({ total: 0, retained: 0, left: 0 });
    const [monthsFilter, setMonthsFilter] = useState<number>(3);

    useEffect(() => {
        if (employeeList) {
            const currentDate = new Date();
            const filteredEmployees = employeeList.filter(employee => {
                const hireDate = employee.employeeInfo?.hireDate ? new Date(employee.employeeInfo.hireDate) : null;
                const monthsSinceHire = hireDate ? (currentDate.getMonth() - hireDate.getMonth() + 12 * (currentDate.getFullYear() - hireDate.getFullYear())) : 0;
                return monthsSinceHire <= monthsFilter;
            });

            const totalCount = filteredEmployees.length;
            const retainedCount = filteredEmployees.filter(employee => {
                const terminationDate = employee.employeeInfo?.terminationDate ? new Date(employee.employeeInfo.terminationDate) : null;
                return !terminationDate || terminationDate > currentDate;
            }).length;
            const leftCount = totalCount - retainedCount;

            setRetentionData({ total: totalCount, retained: retainedCount, left: leftCount });
        }
    }, [employeeList, monthsFilter]);

    if (error) return <div>加载失败{JSON.stringify(error)}</div>;
    if (!employeeList) return <div>加载中...</div>;

    return (
        <div>
            <h1>查询最近几个月的员工离职率</h1>
            <div>
                <label>
                    最近几个月:
                    <input type="number" value={monthsFilter} onChange={(e) => setMonthsFilter(Number(e.target.value))} />
                </label>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
                <thead>
                    <tr style={{ backgroundColor: '#f2f2f2' }}>
                        <th style={{ padding: '10px', border: '1px solid #ddd' }}>总员工数</th>
                        <th style={{ padding: '10px', border: '1px solid #ddd' }}>留存员工数</th>
                        <th style={{ padding: '10px', border: '1px solid #ddd' }}>离职员工数</th>
                        <th style={{ padding: '10px', border: '1px solid #ddd' }}>入职时间</th>
                        <th style={{ padding: '10px', border: '1px solid #ddd' }}>在职时长</th>
                    </tr>
                </thead>
                <tbody>
                    {employeeList.map(employee => {
                        const hireDate = employee.employeeInfo?.hireDate ? new Date(employee.employeeInfo.hireDate) : null;
                        const currentDate = new Date();
                        const monthsSinceHire = hireDate ? (currentDate.getMonth() - hireDate.getMonth() + 12 * (currentDate.getFullYear() - hireDate.getFullYear())) : 0;
                        const years = Math.floor(monthsSinceHire / 12);
                        const months = monthsSinceHire % 12;
                        const duration = `${years}年${months}个月`;

                        return (
                            <tr key={employee.id}>
                                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{retentionData.total}</td>
                                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{retentionData.retained}</td>
                                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{retentionData.left}</td>
                                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{hireDate ? hireDate.toLocaleDateString() : '未知'}</td>
                                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{duration}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}