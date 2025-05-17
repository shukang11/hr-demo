import { useCallback, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
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
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { useCompanyStore } from "@/hooks/use-company-store"
import { Position, InsertPosition, createOrUpdatePosition } from "@/lib/api/position"

const formSchema = z.object({
  id: z.number().optional(),
  name: z.string().min(1, "职位名称不能为空"),
  company_id: z.number(),
  remark: z.string().nullable(),
})

interface PositionFormProps {
  position?: Position | null
  open: boolean
  onClose: () => void
}

export function PositionForm({ position, open, onClose }: PositionFormProps) {
  const { toast } = useToast()
  const { currentCompany } = useCompanyStore()

  const form = useForm<InsertPosition>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      id: position?.id,
      name: position?.name || "",
      company_id: currentCompany?.id || 0,
      remark: position?.remark || "",
    },
  })

  // 当 position 或 open 状态变化时，重置表单的值
  useEffect(() => {
    if (open) {
      form.reset({
        id: position?.id,
        name: position?.name || "",
        company_id: currentCompany?.id || 0,
        remark: position?.remark || "",
      })
    }
  }, [position, open, currentCompany?.id, form])

  const onSubmit = useCallback(async (data: InsertPosition) => {
    try {
      await createOrUpdatePosition(data)
      toast({
        title: "成功",
        description: `${data.id ? "更新" : "创建"}职位成功`,
      })
      onClose()
    } catch (error) {
      console.error("Failed to save position:", error)
      toast({
        variant: "destructive",
        title: "错误",
        description: `${data.id ? "更新" : "创建"}职位失败`,
      })
    }
  }, [onClose, toast])

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{position ? "编辑职位" : "新增职位"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>职位名称</FormLabel>
                  <FormControl>
                    <Input {...field} />
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
                    <Textarea {...field} value={field.value || ''} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose}>
                取消
              </Button>
              <Button type="submit">保存</Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}