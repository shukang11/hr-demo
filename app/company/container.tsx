'use client';

import CompanyHeader from '@/app/company/header';
import { useCompany } from '@/lib/providers/company-provider';
import { Company } from '@/types';

export default function Page() {

    
    const {currentCompany, changeCompany} = useCompany();

    const employeeCount = 100; // 假设公司在职员工人数为100
    const maleRatio = 0.6; // 假设男性比例为60%
    const femaleRatio = 0.4; // 假设女性比例为40%
    const birthdayCount = 5; // 假设本月生日人数为5
    const todoCount = 10; // 假设待办事项为10

    return (
        <>
            <CompanyHeader companyName={currentCompany?.name ?? ""} onEdit={(newName) => {
                if (currentCompany) {
                    changeCompany({ ...currentCompany, name: newName });
                }
            }} />
            <div className="mt-4">
                <p>在职员工人数: {employeeCount}</p>
                <p>男性比例: {maleRatio * 100}%</p>
                <p>女性比例: {femaleRatio * 100}%</p>
                <p>本月生日人数: {birthdayCount}</p>
                <p>待办事项: {todoCount}</p>
            </div>
        </>
    );
}
