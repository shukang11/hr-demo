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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { format } from "date-fns";

import { z } from "zod"
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod"
import { getUUID } from "@/lib/helper";

const FormSchema = z.object({
    uuid: z.string().optional(),
    username: z.string().optional(),
    birthdate: z.date().optional(),
    gender: z.enum(["Male", "Female", "Unknown"]).optional(),
    email: z.string().email().optional(),
    phone: z.string().min(10, {
        message: "至少10位数",
    }).max(15, {
        message: "最多15位数",
    }).optional(),
    address: z.string().optional(),
});

interface ContainerProps {
    onSubmit: (data: z.infer<typeof FormSchema>) => void;
}

export default function InsertMemberForm({ onSubmit }: ContainerProps) {
    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            uuid: getUUID(),
            username: "",
            email: "",
            phone: "",
            birthdate: new Date(),
            address: "",
            gender: 'Unknown',
        }
    });

    return (
        <>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                    <CardSection title="基础信息">
                        <div className="flex space-x-4">
                            <FormField
                                control={form.control}
                                name="username"
                                render={({ field }) => (
                                    <FormItem className="w-1/2">
                                        <FormLabel>姓名</FormLabel>
                                        <FormControl>
                                            <Input placeholder="请输入姓名" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="email"
                                render={({ field }) => (
                                    <FormItem className="w-1/2">
                                        <FormLabel>邮箱</FormLabel>
                                        <FormControl>
                                            <Input placeholder="请输入邮箱" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <div className="flex space-x-4">
                            <FormField
                                control={form.control}
                                name="phone"
                                render={({ field }) => (
                                    <FormItem className="w-1/2">
                                        <FormLabel>手机号</FormLabel>
                                        <FormControl>
                                            <Input placeholder="请输入手机号" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="birthdate"
                                render={({ field }) => (
                                    <FormItem className="w-1/2 flex flex-col">
                                        <FormLabel>出生日期</FormLabel>
                                        <Popover>
                                            <PopoverTrigger asChild>
                                                <FormControl>
                                                    <Button variant="outline" className={cn("text-left font-normal", !field.value && "text-muted-foreground")}>
                                                        {field.value ? format(field.value, "PPP") : <span>选择日期</span>}
                                                    </Button>
                                                </FormControl>
                                            </PopoverTrigger>
                                            <PopoverContent className="w-auto p-0" align="start">
                                                <Calendar
                                                    mode="single"
                                                    selected={field.value}
                                                    onSelect={field.onChange}
                                                    disabled={(date: Date) => date > new Date() || date < new Date("1900-01-01")}
                                                    initialFocus
                                                />
                                            </PopoverContent>
                                        </Popover>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <div className="flex space-x-4">
                            <FormField
                                control={form.control}
                                name="address"
                                render={({ field }) => (
                                    <FormItem className="w-1/2">
                                        <FormLabel>地址</FormLabel>
                                        <FormControl>
                                            <Input placeholder="请输入地址" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="gender"
                                render={({ field }) => (
                                    <FormItem className="w-1/2">
                                        <FormLabel>性别</FormLabel>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="选择性别" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="Male">男</SelectItem>
                                                <SelectItem value="Female">女</SelectItem>
                                                <SelectItem value="Unknown">未知</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </CardSection>

                </form>
            </Form>
        </>
    )
}