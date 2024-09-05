'use client';

import InsertPositionForm from "./insert-position-form";
import { dbAddPosition } from "@/services/position";
import { useRouter } from "next/navigation";

// interface ContainerProps { }

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
            <InsertPositionForm onSubmit={handleSubmit} />
        </>
    )
}