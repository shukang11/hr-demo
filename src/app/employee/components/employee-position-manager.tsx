import { useState } from "react"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { Employee, InsertEmployeePosition, addEmployeePosition, removeEmployeePosition, useEmployeePositions } from "@/lib/api/employee"
import { useDepartments } from "@/lib/api/department"
import { usePositions } from "@/lib/api/position"

interface EmployeePositionManagerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  employee: Employee
}

export function EmployeePositionManager({
  open,
  onOpenChange,
  employee,
}: EmployeePositionManagerProps) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [selectedDepartmentId, setSelectedDepartmentId] = useState<number>()
  const [selectedPositionId, setSelectedPositionId] = useState<number>()

  // 获取员工的职位列表
  const { data: positions, mutate: mutatePositions } = useEmployeePositions(employee.id)
  
  // 获取部门列表
  const { data: departments } = useDepartments(employee.company_id, {
    page: 1,
    limit: 100,
  })

  // 获取职位列表
  const { data: positionList } = usePositions(employee.company_id, {
    page: 1,
    limit: 100,
  })

  // 添加职位
  const handleAddPosition = async () => {
    if (!selectedDepartmentId || !selectedPositionId) {
      toast({
        title: "错误",
        description: "请选择部门和职位",
        variant: "destructive",
      })
      return
    }

    try {
      setLoading(true)
      const data: InsertEmployeePosition = {
        employee_id: employee.id,
        company_id: employee.company_id,
        department_id: selectedDepartmentId,
        position_id: selectedPositionId,
      }
      await addEmployeePosition(data)
      toast({
        title: "成功",
        description: "添加职位成功",
      })
      mutatePositions()
      setSelectedDepartmentId(undefined)
      setSelectedPositionId(undefined)
    } catch (error) {
      console.error("添加职位失败:", error)
      toast({
        title: "错误",
        description: "添加职位失败",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  // 删除职位
  const handleRemovePosition = async (id: number) => {
    try {
      setLoading(true)
      await removeEmployeePosition(id)
      toast({
        title: "成功",
        description: "删除职位成功",
      })
      mutatePositions()
    } catch (error) {
      console.error("删除职位失败:", error)
      toast({
        title: "错误",
        description: "删除职位失败",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>管理职位 - {employee.name}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* 添加职位表单 */}
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">
                选择部门
              </label>
              <Select
                value={selectedDepartmentId?.toString()}
                onValueChange={(value) => setSelectedDepartmentId(Number(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="请选择部门" />
                </SelectTrigger>
                <SelectContent>
                  {departments?.items.map((dept) => (
                    <SelectItem key={dept.id} value={dept.id.toString()}>
                      {dept.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">
                选择职位
              </label>
              <Select
                value={selectedPositionId?.toString()}
                onValueChange={(value) => setSelectedPositionId(Number(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="请选择职位" />
                </SelectTrigger>
                <SelectContent>
                  {positionList?.items.map((pos) => (
                    <SelectItem key={pos.id} value={pos.id.toString()}>
                      {pos.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleAddPosition}
              disabled={loading || !selectedDepartmentId || !selectedPositionId}
            >
              {loading ? <LoadingSpinner className="mr-2" /> : null}
              添加职位
            </Button>
          </div>

          {/* 职位列表 */}
          <div className="border rounded-md">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>部门</TableHead>
                  <TableHead>职位</TableHead>
                  <TableHead>备注</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {!positions ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center">
                      加载中...
                    </TableCell>
                  </TableRow>
                ) : positions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center">
                      暂无职位信息
                    </TableCell>
                  </TableRow>
                ) : (
                  positions.map((pos) => (
                    <TableRow key={pos.id}>
                      <TableCell>
                        {departments?.items.find(
                          (d) => d.id === pos.department_id
                        )?.name ?? "-"}
                      </TableCell>
                      <TableCell>
                        {positionList?.items.find(
                          (p) => p.id === pos.position_id
                        )?.name ?? "-"}
                      </TableCell>
                      <TableCell>{pos.remark || "-"}</TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemovePosition(pos.id)}
                          disabled={loading}
                        >
                          删除
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 