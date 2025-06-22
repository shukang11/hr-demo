import { useState, useEffect } from "react"
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
import { useToast } from "@/hooks/use-toast"
import { useCompanyStore } from "@/hooks/use-company-store"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { createOrUpdateCandidate, useCandidate } from "@/lib/api/candidate"
import { useDepartments } from "@/lib/api/department"
import { usePositions } from "@/lib/api/position"
import { useSchemaList } from "@/lib/api/customfield"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"
import { CustomFieldEditor } from "@/components/customfield/custom-field-editor"

const formSchema = z.object({
  name: z.string().min(1, "请输入姓名"),
  phone: z.string().optional().nullable(),
  email: z.string().email("请输入有效的邮箱").optional().nullable().or(z.literal("")),
  department_id: z.coerce.number().min(1, "请选择部门"),
  position_id: z.coerce.number().min(1, "请选择职位"),
  interview_date: z.string().min(1, "请选择面试日期"),
  interview_time: z.string().optional(),
  remark: z.string().optional().nullable(),
})

interface Props {
  id?: number
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export function CandidateForm({ id, open, onOpenChange, onSuccess }: Props) {
  const { currentCompany } = useCompanyStore()
  const { toast } = useToast()
  const { data: candidate } = useCandidate(id)
  const [customFieldSchemaId, setCustomFieldSchemaId] = useState<number | null>(null)
  const [customFieldValue, setCustomFieldValue] = useState<Record<string, any> | null>(null)

  // 获取该公司"候选人"类型的自定义字段模板列表
  const { data: candidateSchemas = { items: [] } } = useSchemaList(
    "candidate", // 使用小写，与后端API保持一致
    { page: 1, limit: 100 },
    currentCompany?.id,
    true // 包含系统预设
  )

  const { data: departmentData } = useDepartments(currentCompany?.id, {
    page: 1,
    limit: 100,
  })

  const { data: positionData } = usePositions(currentCompany?.id, {
    page: 1,
    limit: 100,
  })
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    values: {
      name: candidate?.name || "",
      phone: candidate?.phone || "",
      email: candidate?.email || "",
      department_id: candidate?.department_id || 0,
      position_id: candidate?.position_id || 0,
      interview_date: candidate?.interview_date ? new Date(candidate.interview_date).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
      interview_time: candidate?.interview_date ? new Date(candidate.interview_date).toISOString().split('T')[1].slice(0, 5) : "",
      remark: candidate?.remark || "",
    },
  })

  // 处理自定义字段的初始化
  useEffect(() => {
    if (!open) {
      // 重置自定义字段状态
      setCustomFieldSchemaId(null)
      setCustomFieldValue(null)
    }
  }, [open])

  useEffect(() => {
    if (open && candidate && id) {
      // 编辑模式：设置自定义字段信息
      if (candidate.extra_schema_id) {
        setCustomFieldSchemaId(candidate.extra_schema_id);
      }

      if (candidate.extra_value) {
        setCustomFieldValue(candidate.extra_value);
      }
    }
  }, [candidate, open, id])

  useEffect(() => {
    if (open) {
      // 新建候选人时，自动选择第一个可用的自定义字段模板
      if (!id && !customFieldSchemaId && candidateSchemas.items.length > 0) {
        const firstAvailableSchema = candidateSchemas.items[0];
        if (firstAvailableSchema) {
          console.log("自动选择候选人自定义字段模板:", firstAvailableSchema.name);
          setCustomFieldSchemaId(firstAvailableSchema.id);
        }
      }

      // 编辑候选人时，如果没有指定自定义字段模板，但有可用模板时，也自动选择
      if (id && !customFieldSchemaId && candidate?.extra_schema_id === null && candidateSchemas.items.length > 0) {
        const firstAvailableSchema = candidateSchemas.items[0];
        if (firstAvailableSchema) {
          console.log("编辑时自动选择候选人自定义字段模板:", firstAvailableSchema.name);
          setCustomFieldSchemaId(firstAvailableSchema.id);
        }
      }
    }
  }, [open, id, customFieldSchemaId, candidate, candidateSchemas])

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    if (!currentCompany?.id) return

    try {
      const interviewDate = values.interview_time
        ? `${values.interview_date}T${values.interview_time}:00.000Z`
        : `${values.interview_date}T00:00:00.000Z`; await createOrUpdateCandidate({
          id: id,
          company_id: currentCompany.id,
          name: values.name,
          phone: values.phone || null,
          email: values.email || null,
          department_id: values.department_id,
          position_id: values.position_id,
          interview_date: interviewDate,
          interviewer_id: null,
          remark: values.remark || null,
          extra_value: customFieldValue || null,
          extra_schema_id: customFieldSchemaId || null,
        })
      toast({
        description: `候选人${id ? "更新" : "创建"}成功`,
      })
      onSuccess()
    } catch (error) {
      console.error('Error:', error);
      toast({
        variant: "destructive",
        description: "操作失败，请重试",
      })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{id ? "编辑" : "添加"}候选人</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>姓名 *</FormLabel>
                  <FormControl>
                    <Input {...field} />
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
                  <FormLabel>联系电话</FormLabel>
                  <FormControl>
                    <Input {...field} value={field.value || ""} />
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
                    <Input {...field} value={field.value || ""} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="department_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>应聘部门 *</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value.toString()}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择部门" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {departmentData?.items.map((department) => (
                        <SelectItem key={department.id} value={department.id.toString()}>
                          {department.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="position_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>应聘职位 *</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value.toString()}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择职位" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {positionData?.items.map((position) => (
                        <SelectItem key={position.id} value={position.id.toString()}>
                          {position.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="interview_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>面试日期 *</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="interview_time"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>面试时间（可选）</FormLabel>
                    <FormControl>
                      <Input type="time" {...field} value={field.value || ""} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>            <FormField
              control={form.control}
              name="remark"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>备注</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="请输入备注信息..."
                      className="resize-none"
                      {...field}
                      value={field.value || ""}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Separator className="my-4" />

            {/* 自定义字段编辑器 */}
            <div className="space-y-4">
              <CustomFieldEditor
                entityType="candidate"
                companyId={currentCompany?.id}
                schemaId={customFieldSchemaId}
                formData={customFieldValue || undefined}
                onSchemaChange={(id) => setCustomFieldSchemaId(id)}
                onFormDataChange={(data) => setCustomFieldValue(data)}
                disabled={false}
                hideSchemaSelector={true}
              />
            </div>

            <Button type="submit">提交</Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
} 