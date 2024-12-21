import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Department, InsertDepartment, createOrUpdateDepartment } from "@/lib/api/department"
import { useToast } from "@/hooks/use-toast"
import { useState } from "react"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

const formSchema = z.object({
  name: z.string().min(1, "部门名称不能为空"),
  parent_id: z.string().optional(),
  leader_id: z.string().optional(),
  remark: z.string().optional(),
})

type DepartmentFormValues = z.infer<typeof formSchema>

interface DepartmentFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
  initialData?: Department | null
  companyId: number
}

export function DepartmentForm({ open, onOpenChange, onSuccess, initialData, companyId }: DepartmentFormProps) {
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const form = useForm<DepartmentFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: initialData?.name ?? "",
      parent_id: initialData?.parent_id?.toString() ?? "",
      leader_id: initialData?.leader_id?.toString() ?? "",
      remark: initialData?.remark ?? "",
    },
  })

  async function onSubmit(values: DepartmentFormValues) {
    try {
      setLoading(true)
      const data: InsertDepartment = {
        id: initialData?.id,
        name: values.name,
        company_id: companyId,
        parent_id: values.parent_id ? parseInt(values.parent_id) : null,
        leader_id: values.leader_id ? parseInt(values.leader_id) : null,
        remark: values.remark || null,
      }
      console.log(`${initialData ? "更新" : "创建"}部门请求:`, data)
      await createOrUpdateDepartment(data)
      toast({
        title: "成功",
        description: `${initialData ? "更新" : "创建"}部门成功`,
      })
      onSuccess?.()
    } catch (error) {
      console.error(`${initialData ? "更新" : "创建"}部门失败:`, error)
      toast({
        title: "错误",
        description: `${initialData ? "更新" : "创建"}部门失败`,
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
          <DialogTitle>{initialData ? "编辑部门" : "新建部门"}</DialogTitle>
        </DialogHeader>

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
              name="parent_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>上级部门</FormLabel>
                  <FormControl>
                    <Input type="number" placeholder="请输入上级部门ID" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="leader_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>负责人</FormLabel>
                  <FormControl>
                    <Input type="number" placeholder="请输入负责人ID" {...field} />
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