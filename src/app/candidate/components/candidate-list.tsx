import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useCompanyStore } from "@/hooks/use-company-store"
import { useToast } from "@/hooks/use-toast"
import { useCandidateList, deleteCandidate, getCandidateStatusText } from "@/lib/api/candidate"
import { useState } from "react"
import { CandidateForm } from "./candidate-form.tsx"
import { CandidateStatusForm } from "./candidate-status-form.tsx"
import { format } from "date-fns"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog"
import { useDepartments } from "@/lib/api/department"
import { usePositions } from "@/lib/api/position"
import { useEmployees } from "@/lib/api/employee"

export function CandidateList() {
  const { currentCompany } = useCompanyStore()
  const { toast } = useToast()
  const [page,] = useState(1)
  const [selectedId, setSelectedId] = useState<number>()
  const [showForm, setShowForm] = useState(false)
  const [showStatusForm, setShowStatusForm] = useState(false)

  const { data: candidateData, mutate } = useCandidateList(currentCompany?.id, {
    page,
    limit: 10,
  })

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

  const handleDelete = async (id: number) => {
    try {
      await deleteCandidate(id)
      toast({
        description: "候选人删除成功",
      })
      mutate()
    } catch (error) {
      toast({
        variant: "destructive",
        description: "操作失败，请重试",
      })
    }
  }

  const getDepartmentName = (id: number) => {
    return departmentData?.items.find((item) => item.id === id)?.name || "-"
  }

  const getPositionName = (id: number) => {
    return positionData?.items.find((item) => item.id === id)?.name || "-"
  }

  const getInterviewerName = (id: number) => {
    return employeeData?.items.find((item) => item.id === id)?.name || "-"
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <div className="text-lg font-medium">候选人列表</div>
        <Button onClick={() => {
          setSelectedId(undefined)
          setShowForm(true)
        }}>添加候选人</Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>姓名</TableHead>
              <TableHead>联系话</TableHead>
              <TableHead>邮箱</TableHead>
              <TableHead>应聘部门</TableHead>
              <TableHead>应聘职位</TableHead>
              <TableHead>面试时间</TableHead>
              <TableHead>面试官</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>备注</TableHead>
              <TableHead>操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {candidateData?.items.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.name}</TableCell>
                <TableCell>{item.phone}</TableCell>
                <TableCell>{item.email || "-"}</TableCell>
                <TableCell>{getDepartmentName(item.department_id)}</TableCell>
                <TableCell>{getPositionName(item.position_id)}</TableCell>
                <TableCell>
                  {item.interview_date ? format(new Date(item.interview_date), "yyyy-MM-dd HH:mm") : "-"}
                </TableCell>
                <TableCell>{getInterviewerName(item.interviewer_id)}</TableCell>
                <TableCell>{getCandidateStatusText(item.status)}</TableCell>
                <TableCell className="max-w-[200px] truncate" title={item.remark || ""}>
                  {item.remark || "-"}
                </TableCell>
                <TableCell className="space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedId(item.id)
                      setShowForm(true)
                    }}
                  >
                    编辑
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedId(item.id)
                      setShowStatusForm(true)
                    }}
                  >
                    更新状态
                  </Button>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="outline" size="sm">
                        删除
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>确认删除</AlertDialogTitle>
                        <AlertDialogDescription>
                          此操作将永久删除该候选人，是否继续？
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>取消</AlertDialogCancel>
                        <AlertDialogAction onClick={() => handleDelete(item.id)}>
                          确认
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <CandidateForm
        open={showForm}
        id={selectedId}
        onOpenChange={setShowForm}
        onSuccess={() => {
          setShowForm(false)
          mutate()
        }}
      />

      <CandidateStatusForm
        open={showStatusForm}
        id={selectedId}
        onOpenChange={setShowStatusForm}
        onSuccess={() => {
          setShowStatusForm(false)
          mutate()
        }}
      />
    </div>
  )
} 