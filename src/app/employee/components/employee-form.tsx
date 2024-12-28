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
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Employee, createOrUpdateEmployee, useEmployee } from "@/lib/api/employee"
import { useDepartments } from "@/lib/api/department"
import { usePositions } from "@/lib/api/position"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { SelectCandidateDialog } from "./select-candidate-dialog"
import { useState, useEffect } from "react"
import { dateToTimestamp } from "@/lib/utils"

const formSchema = z.object({
  name: z.string().min(1, "请输入姓名"),
  phone: z.string().optional().nullable(),
  email: z.string().email("请输入有效的邮箱").optional().nullable().or(z.literal("")),
  department_id: z.coerce.number().optional().nullable(),
  position_id: z.coerce.number().optional().nullable(),
  entry_date: z.number().optional().nullable(),
  birthdate: z.number().optional().nullable(),
  address: z.string().optional().nullable(),
  gender: z.enum(["Male", "Female", "Unknown"]),
})

interface Props {
  id?: number
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
  companyId: number
  initialData?: Employee | null
}

export function EmployeeForm({ id, open, onOpenChange, onSuccess, companyId, initialData }: Props) {
  const { toast } = useToast()
  const { data: employee } = useEmployee(id)
  const [showCandidateDialog, setShowCandidateDialog] = useState(false)

  const { data: departmentData } = useDepartments(companyId, {
    page: 1,
    limit: 100,
  })

  const { data: positionData } = usePositions(companyId, {
    page: 1,
    limit: 100,
  })

  console.log(`employee: ${JSON.stringify(employee)}`)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      phone: "",
      email: "",
      department_id: null,
      position_id: null,
      entry_date: dateToTimestamp(new Date()),
      birthdate: dateToTimestamp(null),
      address: "",
      gender: "Unknown",
    },
  })

  useEffect(() => {
    if (!open) {
      form.reset({
        name: "",
        phone: "",
        email: "",
        department_id: null,
        position_id: null,
        entry_date: dateToTimestamp(new Date()),
        birthdate: dateToTimestamp(null),
        address: "",
        gender: "Unknown",
      })
    }
  }, [open, form])

  useEffect(() => {
    if (open && (employee || initialData) && id) {
      const data = initialData || employee
      form.reset({
        name: data?.name || "",
        phone: data?.phone || "",
        email: data?.email || "",
        department_id: data?.department_id || null,
        position_id: data?.position_id || null,
        entry_date: dateToTimestamp(new Date()),
        birthdate: data?.birthdate || dateToTimestamp(null),
        address: data?.address || "",
        gender: data?.gender || "Unknown",
      })
    }
  }, [employee, initialData, form, open, id])

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      await createOrUpdateEmployee({
        id: id,
        company_id: companyId,
        name: values.name,
        phone: values.phone || null,
        email: values.email || null,
        department_id: values.department_id,
        position_id: values.position_id,
        entry_date: values.entry_date,
        birthdate: values.birthdate || null,
        address: values.address || null,
        gender: values.gender,
        extra_value: null,
        extra_schema_id: null,
      })
      toast({
        description: `员工${id ? "更新" : "创建"}成功`,
      })
      onSuccess()
      onOpenChange(false)
    } catch (error) {
      console.error('Error:', error);
      toast({
        variant: "destructive",
        description: "操作失败，请重试",
      })
    }
  }

  const handleSelectCandidate = (candidate: any) => {
    form.setValue("name", candidate.name)
    form.setValue("phone", candidate.phone || "")
    form.setValue("email", candidate.email || "")
    form.setValue("department_id", candidate.department_id)
    form.setValue("position_id", candidate.position_id)
    form.setValue("gender", "Unknown")
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <DialogHeader className="flex flex-row items-center justify-between border-b pb-4">
            <DialogTitle className="text-xl">{id ? "编辑" : "添加"}员工</DialogTitle>
            {!id && (
              <Button
                variant="outline"
                onClick={() => setShowCandidateDialog(true)}
                className="gap-2"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <line x1="19" x2="19" y1="8" y2="14" />
                  <line x1="22" x2="16" y1="11" y2="11" />
                </svg>
                从候选人导入
              </Button>
            )}
          </DialogHeader>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 py-4">
              <div className="grid grid-cols-2 gap-4">
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
              </div>

              <div className="grid grid-cols-2 gap-4">
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
              </div>

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="birthdate"
                  render={({ field: { value, onChange, ...field } }) => (
                    <FormItem>
                      <FormLabel>出生日期</FormLabel>
                      <FormControl>
                        <Input 
                          type="date" 
                          {...field}
                          value={value ? new Date(value).toISOString().split('T')[0] : ""}
                          onChange={(e) => {
                            const date = e.target.value ? dateToTimestamp(new Date(e.target.value)) : null
                            onChange(date)
                          }}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="entry_date"
                  render={({ field: { value, onChange, ...field } }) => (
                    <FormItem>
                      <FormLabel>入职日期</FormLabel>
                      <FormControl>
                        <Input 
                          type="date" 
                          {...field}
                          value={value ? new Date(value).toISOString().split('T')[0] : ""}
                          onChange={(e) => {
                            const date = e.target.value ? dateToTimestamp(new Date(e.target.value)) : null
                            onChange(date)
                          }}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>地址</FormLabel>
                    <FormControl>
                      <Input {...field} value={field.value || ""} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="department_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>所属部门</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value?.toString() || undefined}>
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
                      <FormLabel>职位</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value?.toString() || undefined}>
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
              </div>

              <div className="flex justify-end">
                <Button type="submit">
                  {id ? "更新" : "创建"}
                </Button>
              </div>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      <SelectCandidateDialog
        open={showCandidateDialog}
        onOpenChange={setShowCandidateDialog}
        onSelect={handleSelectCandidate}
      />
    </>
  )
} 