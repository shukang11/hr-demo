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
import {  Employee } from "@/types";
import { useDepartments } from "@/services/department";
import { usePositions } from "@/services/position";
import { useCompany } from "@/lib/providers/company-provider";
import { useEmployees } from "@/services/employ";

const InsertMemberFormSchema = z.object({
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
    departmentId: z.string().optional(),
    positionId: z.string().optional(),

});

interface ContainerProps {
    data?: Employee;
    onSubmit: (_data: Employee) => void;
}

export default function InsertMemberForm({ data, onSubmit }: ContainerProps) {
    const isInsert = data === undefined;
    const { currentCompany } = useCompany();
    const { data: employeeList } = useEmployees();
    const { data: departmentList } = useDepartments();
    const { data: positionList } = usePositions();
    
    const form = useForm<z.infer<typeof InsertMemberFormSchema>>({
        resolver: zodResolver(InsertMemberFormSchema),
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

    const submitAction = async (data: z.infer<typeof InsertMemberFormSchema>) => {
        // 
        const employee: Employee = {
            uuid: data.uuid,
            username: data.username ?? "",
            birthdate: data.birthdate ?? new Date(),
            // @ts-ignore
            gender: data.gender ?? "Unknown",
            email: data.email ?? "",
            phone: data.phone ?? "",
            address: data.address ?? "",
            company: currentCompany ?? undefined,
            department: departmentList?.find(d => d.id?.toString() === data.departmentId),
            position: positionList?.find(p => p.id?.toString() === data.positionId),
        };

        if (isInsert) {
            const emailExists = employeeList?.some(e => e.email === employee.email);
            const phoneExists = employeeList?.some(e => e.phone === employee.phone);
            const usernameExists = employeeList?.some(e => e.username === employee.username);

            if (employee.username && usernameExists) {
                form.setError("username", {
                    type: "manual",
                    message: "姓名已存在",
                });
                return;
            }
            
            if (employee.email && emailExists) {
                form.setError("email", {
                    type: "manual",
                    message: "邮箱已存在",
                });
                return;
            }

            if (employee.phone && phoneExists) {
                form.setError("phone", {
                    type: "manual",
                    message: "手机号已存在",
                });
                return;
            }

        }

        onSubmit(employee);
    }

    return (
        <>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(submitAction)} className="space-y-8">
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
                                    <FormItem className="w-1/2">
                                        <FormLabel>出生日期</FormLabel>
                                        <Popover>
                                            <PopoverTrigger asChild>
                                                <FormControl>
                                                    <Button variant="outline" className={cn("w-full text-left font-normal", !field.value && "text-muted-foreground")}>
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
                        <div className="flex space-x-4">
                            <FormField
                                control={form.control}
                                name="departmentId"
                                render={({ field }) => (
                                    <FormItem className="w-1/2">
                                        <FormLabel>部门</FormLabel>
                                        <Select onValueChange={val => field.onChange(val)} defaultValue={field.value?.toString()}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="选择部门" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                {departmentList?.map(department => (
                                                    <SelectItem key={department.id} value={department.id?.toString() || ''}>{department.name}</SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="positionId"
                                render={({ field }) => (
                                    <FormItem className="w-1/2">
                                        <FormLabel>职位</FormLabel>
                                        <Select onValueChange={val => field.onChange(val)} defaultValue={field.value?.toString()}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="选择职位" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                {positionList?.map(position => (
                                                    <SelectItem key={position.id} value={position.id?.toString() || ''}>{position.name}</SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
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
    )
}