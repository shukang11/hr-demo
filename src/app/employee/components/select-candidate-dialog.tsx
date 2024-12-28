import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { useCompanyStore } from "@/hooks/use-company-store"
import { useCandidateList } from "@/lib/api/candidate"
import { useState } from "react"
import { format } from "date-fns"
import { useDepartments } from "@/lib/api/department"
import { usePositions } from "@/lib/api/position"
import { Search } from "lucide-react"

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSelect: (candidate: any) => void
}

export function SelectCandidateDialog({ open, onOpenChange, onSelect }: Props) {
  const { currentCompany } = useCompanyStore()
  const [search, setSearch] = useState("")
  const [page, setPage] = useState(1)

  const { data: candidateData } = useCandidateList(currentCompany?.id, {
    page,
    limit: 10,
    status: "通过",
    search,
  })

  const { data: departmentData } = useDepartments(currentCompany?.id, {
    page: 1,
    limit: 100,
  })

  const { data: positionData } = usePositions(currentCompany?.id, {
    page: 1,
    limit: 100,
  })

  const getDepartmentName = (id: number) => {
    return departmentData?.items.find((item) => item.id === id)?.name || "-"
  }

  const getPositionName = (id: number) => {
    return positionData?.items.find((item) => item.id === id)?.name || "-"
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>选择候选人</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜索候选人姓名..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8"
            />
          </div>

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/50">
                  <TableHead className="w-[120px]">姓名</TableHead>
                  <TableHead className="w-[120px]">联系电话</TableHead>
                  <TableHead className="w-[180px]">邮箱</TableHead>
                  <TableHead className="w-[120px]">应聘部门</TableHead>
                  <TableHead className="w-[120px]">应聘职位</TableHead>
                  <TableHead className="w-[120px]">面试时间</TableHead>
                  <TableHead className="w-[100px]">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {candidateData?.items.map((item) => (
                  <TableRow key={item.id} className="hover:bg-muted/50">
                    <TableCell className="font-medium">{item.name}</TableCell>
                    <TableCell>{item.phone || "-"}</TableCell>
                    <TableCell>{item.email || "-"}</TableCell>
                    <TableCell>{getDepartmentName(item.department_id)}</TableCell>
                    <TableCell>{getPositionName(item.position_id)}</TableCell>
                    <TableCell>
                      {item.interview_date ? format(new Date(item.interview_date), "yyyy-MM-dd") : "-"}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          onSelect(item)
                          onOpenChange(false)
                        }}
                      >
                        选择
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {(!candidateData?.items || candidateData.items.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={7} className="h-24 text-center">
                      暂无数据
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 