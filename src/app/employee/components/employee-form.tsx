import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Employee, InsertEmployee, createOrUpdateEmployee, Gender } from "@/lib/api/employee"
import { useEffect, useState } from "react"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

const formSchema = z.object({
  name: z.string().min(1, "姓名不能为空"),
  email: z.string().email("邮箱格式不正确").optional().or(z.literal("")),
  phone: z.string().optional().or(z.literal("")),
  birthdate: z.string().optional().or(z.literal("")),
  address: z.string().optional().or(z.literal("")),
  gender: z.enum(["Male", "Female", "Unknown"] as const),
  extra_value: z.any().optional(),
  extra_schema_id: z.number().optional().nullable(),
})

type EmployeeFormValues = z.infer<typeof formSchema>

interface EmployeeFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
  initialData?: Employee | null
  companyId: number
}

export function EmployeeForm({ open, onOpenChange, onSuccess, initialData, companyId }: EmployeeFormProps) {
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const form = useForm<EmployeeFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      birthdate: "",
      address: "",
      gender: "Unknown",
      extra_value: null,
      extra_schema_id: null,
    },
  })

  useEffect(() => {
    if (initialData) {
      form.reset({
        name: initialData.name,
        email: initialData.email ?? "",
        phone: initialData.phone ?? "",
        birthdate: initialData.birthdate ? initialData.birthdate.split('T')[0] : "",
        address: initialData.address ?? "",
        gender: initialData.gender,
        extra_value: initialData.extra_value ?? null,
        extra_schema_id: initialData.extra_schema_id ?? null,
      })
    } else {
      form.reset({
        name: "",
        email: "",
        phone: "",
        birthdate: "",
        address: "",
        gender: "Unknown",
        extra_value: null,
        extra_schema_id: null,
      })
    }
  }, [form, initialData])

  async function onSubmit(values: EmployeeFormValues) {
    try {
      setLoading(true)
      const data: InsertEmployee = {
        id: initialData?.id,
        company_id: companyId,
        name: values.name,
        email: values.email || null,
        phone: values.phone || null,
        birthdate: values.birthdate ? `${values.birthdate}T00:00:00Z` : null,
        address: values.address || null,
        gender: values.gender as Gender,
        extra_value: values.extra_value || null,
        extra_schema_id: values.extra_schema_id || null,
      }
      await createOrUpdateEmployee(data)
      toast({
        title: "成功",
        description: `${initialData ? "更新" : "创建"}员工成功`,
      })
      onSuccess?.()
      onOpenChange(false)
    } catch (error) {
      console.error(`${initialData ? "更新" : "创建"}员工失败:`, error)
      toast({
        title: "错误",
        description: `${initialData ? "更新" : "创建"}员工失败`,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{initialData ? "编辑员工" : "新建员工"}</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
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
                <FormItem>
                  <FormLabel>邮箱</FormLabel>
                  <FormControl>
                    <Input type="email" placeholder="请输入邮箱" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>电话</FormLabel>
                  <FormControl>
                    <Input type="tel" placeholder="请输入电话" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="birthdate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>出生日期</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="address"
              render={({ field }) => (
                <FormItem>
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
                <FormItem>
                  <FormLabel>性别</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择性别" />
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

            <div className="flex justify-end space-x-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={loading}
              >
                取消
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? <LoadingSpinner className="mr-2" /> : null}
                确定
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
} 