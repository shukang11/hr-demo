'use client';

import CardSection from "@/components/card-section";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useCompany } from "@/lib/providers/company-provider";

const InsertPositionFormSchema = z.object({
    name: z.string().min(1, { message: "职位名称不能为空" }),
    company_id: z.number().int().positive({ message: "公司ID必须为正整数" }),
    remark: z.string().optional(),
});

interface InsertPositionFormProps {
    onSubmit: (data: z.infer<typeof InsertPositionFormSchema>) => void;
}

export default function InsertPositionForm({ onSubmit }: InsertPositionFormProps) {
    const { currentCompany } = useCompany();
    const form = useForm<z.infer<typeof InsertPositionFormSchema>>({
        resolver: zodResolver(InsertPositionFormSchema),
        defaultValues: {
            name: "",
            company_id: currentCompany?.id, // 假设默认公司ID为1
            remark: "",
        },
    });

    return (
        <>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                    <CardSection title="职位信息">
                        <div className="flex space-x-4">
                            <FormField
                                control={form.control}
                                name="name"
                                render={({ field }) => (
                                    <FormItem className="w-full">
                                        <FormLabel>职位名称</FormLabel>
                                        <FormControl>
                                            <Input placeholder="请输入职位名称" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <div className="flex space-x-4">
                            <FormField
                                control={form.control}
                                name="remark"
                                render={({ field }) => (
                                    <FormItem className="w-full">
                                        <FormLabel>备注</FormLabel>
                                        <FormControl>
                                            <Input placeholder="请输入备注" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </CardSection>
                    <div className="flex space-x-4">
                        <Button type="submit">提交</Button>
                    </div>
                </form>
            </Form>
        </>
    );
}

