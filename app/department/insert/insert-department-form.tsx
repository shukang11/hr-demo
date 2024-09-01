'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Department } from '@/types';
import { useDepartments } from '@/services/department';

export const InsertDepartmentFormSchema = z.object({
  name: z.string().min(1, { message: "部门名称是必填的" }),
  remark: z.string().optional(),
});

interface InsertDepartmentFormProps {
  department?: Department;
  onSubmit: (data: z.infer<typeof InsertDepartmentFormSchema>) => void;

}

export default function InsertDepartmentForm({ department, onSubmit }: InsertDepartmentFormProps) {
  const {data: departments} = useDepartments();

  const form = useForm<z.infer<typeof InsertDepartmentFormSchema>>({
    resolver: zodResolver(InsertDepartmentFormSchema.refine((data) => {
      return !departments?.some(dep => dep.name === data.name);
    }, {
      message: "部门名称已存在",
      path: ["name"]
    })),
    defaultValues: {
      name: department?.name || "",
      remark: department?.remark || "",
    },
  });



  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>部门名称</FormLabel>
              <FormControl>
                <Input placeholder="请输入部门名称" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="remark"
          render={({ field }) => (
            <FormItem>
              <FormLabel>备注</FormLabel>
              <FormControl>
                <Input placeholder="请输入备注" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">提交</Button>
      </form>
    </Form>
  );
}