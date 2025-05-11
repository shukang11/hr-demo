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
import { Company, InsertCompany, createOrUpdateCompany, useCompanies } from "@/lib/api/company"
import { useToast } from "@/hooks/use-toast"
import { useEffect, useState } from "react"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { CustomFieldEditor } from "@/components/customfield"
import { Separator } from "@/components/ui/separator"

const formSchema = z.object({
  name: z.string().min(1, "公司名称不能为空"),
  description: z.string().optional(),
  parent_id: z.number().nullable().optional(),
  extra_value: z.any().optional(),
  extra_schema_id: z.number().nullable().optional(),
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
      description: initialData?.description ?? "",
      parent_id: initialData?.parent_id ?? null,
      extra_value: initialData?.extra_value,
      extra_schema_id: initialData?.extra_schema_id ?? null,
    },
  })
  // 获取公司列表（用于选择父公司）
  const { data: companiesData } = useCompanies({ page: 1, limit: 100 })

  // 监听 initialData 变化，重置表单值
  useEffect(() => {
    if (initialData) {
      form.reset({
        name: initialData.name,
        description: initialData.description || "",
        parent_id: initialData.parent_id || null,
        extra_value: initialData.extra_value,
        extra_schema_id: initialData.extra_schema_id ?? null,
      })
    } else {
      form.reset({
        name: "",
        description: "",
        parent_id: null,
        extra_value: undefined,
        extra_schema_id: null,
      })
    }
  }, [form, initialData])

  async function onSubmit(values: CompanyFormValues) {
    try {
      setLoading(true)
      const data: InsertCompany = {
        ...values,
        id: initialData?.id,
        extra_schema_id: values.extra_schema_id || undefined,
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

  // 处理Schema变更
  const handleSchemaChange = (schemaId: number | null) => {
    form.setValue("extra_schema_id", schemaId);
    // 如果切换了Schema，清空之前的值
    if (form.getValues("extra_schema_id") !== schemaId) {
      form.setValue("extra_value", {});
    }
  };

  // 处理表单数据变更
  const handleFormDataChange = (formData: Record<string, any>) => {
    form.setValue("extra_value", formData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>{initialData ? "编辑公司" : "新建公司"}</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">            <FormField
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

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>公司描述</FormLabel>
                  <FormControl>
                    <Input placeholder="请输入公司描述" {...field} />
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
                  <FormLabel>父公司</FormLabel>
                  <FormControl>
                    <select
                      className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      {...field}
                      value={field.value ?? ""}
                      onChange={(e) => {
                        const value = e.target.value ? Number(e.target.value) : null;
                        field.onChange(value);
                      }}
                    >
                      <option value="">-- 无父公司（作为主公司） --</option>
                      {companiesData?.items?.filter(c => c.id !== initialData?.id).map((company) => (
                        <option key={company.id} value={company.id}>
                          {company.name}
                        </option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Separator className="my-6" />

            <div className="space-y-2">
              <h3 className="text-sm font-medium">自定义字段</h3>
              <p className="text-sm text-muted-foreground">
                选择一个模板来添加公司的自定义信息
              </p>

              <CustomFieldEditor
                entityType="Company"
                entityId={initialData?.id}
                companyId={initialData?.id}
                schemaId={form.watch("extra_schema_id")}
                onSchemaChange={handleSchemaChange}
                formData={form.watch("extra_value")}
                onFormDataChange={handleFormDataChange}
                disabled={loading}
              />
            </div>

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