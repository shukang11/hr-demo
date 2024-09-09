'use client';

import CompanyHeader from '@/app/company/header';
import { useCompany } from '@/lib/providers/company-provider';
import { Company, Employee } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useEmployees } from '@/services/employ';
import { useDepartments } from '@/services/department';
import { usePositions } from '@/services/position';
import { useEffect, useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

export default function Page() {
    const { currentCompany, changeCompany } = useCompany();
    const { data: employeeList, error: employeeError } = useEmployees();
    const { data: departmentList, error: departmentError } = useDepartments();
    const { data: positionList, error: positionError } = usePositions();
    const currentDate = new Date();
    // active employee

    var activeEmployeeList = [];
    if (employeeList) {
        activeEmployeeList = employeeList?.filter((e) => new Employee(e).isActive(currentDate));
    }

    return (
        <>
            <CompanyHeader companyName={currentCompany?.name ?? ""} onEdit={(newName) => {
                if (currentCompany) {
                    changeCompany({ ...currentCompany, name: newName });
                }
            }} />
            <div className="grid grid-cols-2 gap-4 mt-4">
                <Card>
                    <CardHeader>
                        <CardTitle>职位员工数量</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {positionList && (
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>职位名称</TableHead>
                                        <TableHead>在职员工数量</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {positionList.map((position) => {
                                        const positionEmployees = employeeList?.filter((employee) => employee.position?.id === position.id);
                                        const activePositionEmployees = positionEmployees?.filter((employee) => new Employee(employee).isActive(currentDate));
                                        return (
                                            <TableRow key={position.id}>
                                                <TableCell>{position.name}</TableCell>
                                                <TableCell>{activePositionEmployees?.length || 0}</TableCell>
                                            </TableRow>
                                        );
                                    })}
                                </TableBody>
                            </Table>
                        )}
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle>部门员工数量</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {departmentList && (
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>部门名称</TableHead>
                                        <TableHead>在职员工数量</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {departmentList.map((department) => {
                                        const departmentEmployees = employeeList?.filter((employee) => employee.department?.id === department.id);
                                        const activeDepartmentEmployees = departmentEmployees?.filter((employee) => new Employee(employee).isActive(currentDate));
                                        return (
                                            <TableRow key={department.id}>
                                                <TableCell>{department.name}</TableCell>
                                                <TableCell>{activeDepartmentEmployees?.length || 0}</TableCell>
                                            </TableRow>
                                        );
                                    })}
                                </TableBody>
                            </Table>
                        )}
                    </CardContent>
                </Card>
            </div>
        </>
    );
}