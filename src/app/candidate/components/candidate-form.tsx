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
import { useEmployees } from "@/lib/api/employee"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const formSchema = z.object({
  name: z.string().min(1, "请输入姓名"),
  phone: z.string().optional().nullable(),
  email: z.string().email("请输入有效的邮箱").optional().nullable().or(z.literal("")),
  department_id: z.coerce.number().min(1, "请选择部门"),
  position_id: z.coerce.number().min(1, "请选择职位"),
  interview_date: z.string().min(1, "请选择面试时间"),
  interviewer_id: z.coerce.number().optional().nullable(),
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

  const { data: departmentData } = useDepartments(currentCompany?.id, {
    page: 1,
    limit: 100,
  })

  const { data: positionData } = usePositions(currentCompany?.id, {
    page: 1,
    limit: 100,
  })

  const { data: employeeData } = useEmployees(currentCompany?.id, {
    page: 1,
    limit: 100,
  })

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: candidate?.name || "",
      phone: candidate?.phone || "",
      email: candidate?.email || "",
      department_id: candidate?.department_id || 0,
      position_id: candidate?.position_id || 0,
      interview_date: candidate?.interview_date || new Date().toISOString().slice(0, 16),
      interviewer_id: candidate?.interviewer_id || 0,
    },
  })

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    if (!currentCompany?.id) return

    try {
      const interviewDate = new Date(values.interview_date).toISOString();

      await createOrUpdateCandidate({
        id: id,
        company_id: currentCompany.id,
        name: values.name,
        phone: values.phone || null,
        email: values.email || null,
        department_id: values.department_id,
        position_id: values.position_id,
        interview_date: interviewDate,
        interviewer_id: values.interviewer_id === 0 ? null : values.interviewer_id,
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

            <FormField
              control={form.control}
              name="interview_date"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>面试时间 *</FormLabel>
                  <FormControl>
                    <Input type="datetime-local" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="interviewer_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>面试官</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value?.toString() || ""}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择面试官" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {employeeData?.items.map((employee) => (
                        <SelectItem key={employee.id} value={employee.id.toString()}>
                          {employee.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit">提交</Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
} 