'use client';

import InsertMemberForm from "./insert-member-form";
import { dbAddEmployee } from "@/services/employ";
import { useRouter } from "next/navigation";

// interface ContainerProps { }

export default function Container() {
    const router = useRouter();
    // @ts-ignore
    const handleSubmit = async (data) => {
        console.log(`insert member data: ${JSON.stringify(data)}`);
        // [Log] insert member data: {"uuid":"db9e40b3-b0c5-49be-8eee-b0129b66df9e","username":"呀哈哈","birthdate":"2024-09-05T11:17:47.010Z","gender":"Female","email":"test@email.com","phone":"13455555555","address":"","department_id":1,"position_id":1}

        try {
            await dbAddEmployee(data);
            router.back(); // 假设添加成功后跳转到成员列表页面
        } catch (error) {
            console.error("Failed to add member:", error);
        }
    };

    return (
        <>
            <InsertMemberForm onSubmit={handleSubmit} />
        </>
    )
}