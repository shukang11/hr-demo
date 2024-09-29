'use client';

import { z } from "zod";
import InsertDepartmentForm, { InsertDepartmentFormSchema } from "./insert-department-form";
import { dbAddDepartment } from "@/services/department";
import { useCompany } from "@/lib/providers/company-provider";
import { useRouter } from "next/navigation";
import Breadcrumb, { BreadcrumbItem } from "@/components/ui/breadcrumb";
import { MAIN_APP } from "@/lib/routes";

const BreadCrumbItems: BreadcrumbItem[] = [
    { href: MAIN_APP.department.root, label: "部门列表" }
];

export default function Container() {
    const { currentCompany } = useCompany();
    const router = useRouter();

    const onSubmitAction: (data: z.infer<typeof InsertDepartmentFormSchema>) => void = (data) => {
        if (currentCompany) {
            dbAddDepartment({
                name: data.name,
                remark: data.remark,
                company: currentCompany
            });
            router.back();
        } else {
            console.error("No current company selected.");
        }
    }
    return (
        <>
            <Breadcrumb items={BreadCrumbItems} />
            <InsertDepartmentForm department={undefined} onSubmit={(data) => { onSubmitAction(data) }} />
        </>
    )
}