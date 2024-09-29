'use client';

import InsertPositionForm from "./insert-position-form";
import { dbAddPosition } from "@/services/position";
import { useRouter } from "next/navigation";
import Breadcrumb, { BreadcrumbItem } from "@/components/ui/breadcrumb";
import { MAIN_APP } from "@/lib/routes";

const BreadCrumbItems: BreadcrumbItem[] = [
    { href: MAIN_APP.position.root, label: "职位列表" }
];

export default function Container() {
    const router = useRouter();
    // @ts-ignore
    const handleSubmit = async (data) => {
        try {
            await dbAddPosition(data);
            router.back(); // 假设添加成功后跳转到成员列表页面
        } catch (error) {
            console.error("Failed to add member:", error);
        }
    };

    return (
        <>
            <Breadcrumb items={BreadCrumbItems} />
            <InsertPositionForm onSubmit={handleSubmit} />
        </>
    )
}