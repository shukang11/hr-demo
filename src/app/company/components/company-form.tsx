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
import { Company, InsertCompany, createOrUpdateCompany } from "@/lib/api/company"
import { useToast } from "@/hooks/use-toast"
import { useEffect, useState } from "react"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

const formSchema = z.object({
  name: z.string().min(1, "公司名称不能为空"),
  extra_value: z.any().optional(),
  extra_schema_id: z.number().optional(),
})

type CompanyFormValues = z.infer<typeof formSchema>

interface CompanyFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
  initialData?: Company | null
}

export function CompanyForm({ open, onOpenChange, onSuccess, initialData }: CompanyFormProps) {
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const form = useForm<CompanyFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: initialData?.name ?? "",
      extra_value: initialData?.extra_value,
      extra_schema_id: initialData?.extra_schema_id,
    },
  })

  // 监听 initialData 变化，重置表单值
  useEffect(() => {
    if (initialData) {
      form.reset({
        name: initialData.name,
        extra_value: initialData.extra_value,
        extra_schema_id: initialData.extra_schema_id,
      })
    } else {
      form.reset({
        name: "",
        extra_value: undefined,
        extra_schema_id: undefined,
      })
    }
  }, [form, initialData])

  async function onSubmit(values: CompanyFormValues) {
    try {
      setLoading(true)
      const data: InsertCompany = {
        ...values,
        id: initialData?.id,
      }
      await createOrUpdateCompany(data)
      toast({
        title: "成功",
        description: `${initialData ? "更新" : "创建"}公司成功`,
      })
      onSuccess?.()
    } catch (error) {
      console.error(`${initialData ? "更新" : "创建"}公司失败:`, error)
      toast({
        title: "错误",
        description: `${initialData ? "更新" : "创建"}公司失败`,
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
          <DialogTitle>{initialData ? "编辑公司" : "新建公司"}</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>公司名称</FormLabel>
                  <FormControl>
                    <Input placeholder="请输入公司名称" {...field} />
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