'use client';

import React, { useEffect, useState } from 'react';
import { useEmployees } from '@/services/employ';
import { Employee } from '@/types';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

interface MonthlyData {
    /**
     * 每月数据接口
     * @property {number} hired - 每月入职人数
     * @property {number} left - 每月离职人数
     * @property {number} retained - 每月留存人数
     */
    hired: number;
    left: number;
    retained: number;
}

export default function Page() {
    // 获取员工数据和错误状态
    const { data: employeeList, error } = useEmployees();

    // 设置月份过滤器和每月数据的初始状态
    const [monthsFilter, setMonthsFilter] = useState<number>(6);
    const [monthlyData, setMonthlyData] = useState<{ [key: string]: MonthlyData }>({});

    useEffect(() => {
        if (employeeList === undefined) {
            return;
        }
        if (!employeeList) {
            return;
        }
        const currentDate = new Date();
        const filteredData: { [key: string]: MonthlyData } = {};

        for (let i = 0; i < monthsFilter; i++) {
            const monthDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
            const monthKey = format(monthDate, 'yyyy-MM');
            filteredData[monthKey] = { hired: 0, left: 0, retained: 0 };
        }

        for (let i = 0; i < monthsFilter; i++) {
            const monthDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
            const monthKey = format(monthDate, 'yyyy-MM');

            const startOfMonth = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1);
            const endOfMonth = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0);

            employeeList.forEach(employee => {
                const emp = new Employee(employee);

                if (emp.isActive(endOfMonth)) {
                    filteredData[monthKey].retained += 1;
                }

                if (emp.employeeInfo?.hireDate && emp.employeeInfo.hireDate >= startOfMonth && emp.employeeInfo.hireDate <= endOfMonth) {
                    filteredData[monthKey].hired += 1;
                }

                if (emp.employeeInfo?.terminationDate && emp.employeeInfo.terminationDate >= startOfMonth && emp.employeeInfo.terminationDate <= endOfMonth) {
                    filteredData[monthKey].left += 1;
                }

            });
            setMonthlyData(filteredData);
        }

    }, [employeeList, monthsFilter]);

    // 如果加载失败，显示错误信息
    if (error) return <div>加载失败{JSON.stringify(error)}</div>;
    // 如果数据还在加载中，显示加载中提示
    if (!employeeList) return <div>加载中...</div>;

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4">查询最近几个月的员工离职率</h1>
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">
                    最近几个月:
                    <input
                        type="number"
                        value={monthsFilter}
                        onChange={(e) => setMonthsFilter(Number(e.target.value))}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                </label>
            </div>
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            月份
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            入职人数
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            离职人数
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            留存人数
                        </th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {Object.keys(monthlyData).map(month => {
                        const monthData = monthlyData[month];
                        return (
                            <tr key={month}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{month}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{monthData.hired}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{monthData.left}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{monthData.retained}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}