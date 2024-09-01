'use client';

import { z } from "zod";
import InsertDepartmentForm, { InsertDepartmentFormSchema } from "./insert-department-form";
import { dbAddDepartment } from "@/services/department";


interface ContainerProps {
}

export default function Container() {

    const onSubmitAction: (data: z.infer<typeof InsertDepartmentFormSchema>) => void = (data) => {
        dbAddDepartment({
            name: data.name,
            remark: data.remark
        })
        console.log(`data: ${data}`);
    }
    return (
        <>
            <InsertDepartmentForm department={undefined} onSubmit={(data) => { onSubmitAction(data) }} />
        </>
    )
}