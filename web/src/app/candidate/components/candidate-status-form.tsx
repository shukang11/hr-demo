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
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { updateCandidateStatus, useCandidate, CandidateStatus, getCandidateStatusOptions } from "@/lib/api/candidate"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useEffect } from "react"

const formSchema = z.object({
  status: z.nativeEnum(CandidateStatus),
  evaluation: z.string().optional().nullable(),
  remark: z.string().optional().nullable(),
})

interface Props {
  id?: number
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export function CandidateStatusForm({ id, open, onOpenChange, onSuccess }: Props) {
  const { toast } = useToast()
  const { data: candidate } = useCandidate(id)
  const statusOptions = getCandidateStatusOptions()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      status: CandidateStatus.Pending,
      evaluation: "",
      remark: "",
    },
  })

  useEffect(() => {
    if (candidate) {
      form.reset({
        status: candidate.status,
        evaluation: candidate.evaluation || "",
        remark: candidate.remark || "",
      })
    }
  }, [candidate, form])

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    if (!id) return

    try {
      await updateCandidateStatus(id, values)
      toast({
        description: "状态更新成功",
      })
      onSuccess()
    } catch (error) {
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
          <DialogTitle>更新候选人状态</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>状态</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择状态" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {statusOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
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
              name="evaluation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>评价</FormLabel>
                  <FormControl>
                    <Textarea {...field} value={field.value || ""} />
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
                    <Textarea {...field} value={field.value || ""} />
                  </FormControl>
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