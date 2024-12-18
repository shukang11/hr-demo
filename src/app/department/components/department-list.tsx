import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useState, useEffect } from "react"
import { DepartmentForm } from "./department-form"
import { Department, deleteDepartment, getDepartmentList } from "@/lib/api/department"
import { PageParams } from "@/lib/types"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { useToast } from "@/hooks/use-toast"

interface DepartmentListProps {
  companyId: number
}

export function DepartmentList({ companyId }: DepartmentListProps) {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [currentDepartment, setCurrentDepartment] = useState<Department | null>(null)
  const [pageParams, setPageParams] = useState<PageParams>({
    page: 1,
    limit: 10,
  })
  const [total, setTotal] = useState(0)
  const { toast } = useToast()

  const loadData = async () => {
    try {
      setLoading(true)
      const result = await getDepartmentList(companyId, pageParams)
      setDepartments(result.items)
      setTotal(result.total)
    } catch (error) {
      console.error("加载部门列表失败:", error)
      toast({
        title: "错误",
        description: "加载部门列表失败",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [pageParams, companyId])

  const handleEdit = (department: Department) => {
    setCurrentDepartment(department)
    setIsFormOpen(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm("确定要删除这个部门吗？")) {
      return
    }

    try {
      await deleteDepartment(id)
      toast({
        title: "成功",
        description: "删除部门成功",
      })
      loadData()
    } catch (error) {
      console.error("删除部门失败:", error)
      toast({
        title: "错误",
        description: "删除部门失败",
        variant: "destructive",
      })
    }
  }

  const handleFormClose = () => {
    setIsFormOpen(false)
    setCurrentDepartment(null)
  }

  const handleFormSuccess = () => {
    handleFormClose()
    loadData()
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">部门列表</h2>
        <Button onClick={() => setIsFormOpen(true)}>新建部门</Button>
      </div>

      {loading ? (
        <div className="flex justify-center p-8">
          <LoadingSpinner />
        </div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>部门名称</TableHead>
              <TableHead>上级部门</TableHead>
              <TableHead>负责人</TableHead>
              <TableHead>备注</TableHead>
              <TableHead>创建时间</TableHead>
              <TableHead>更新时间</TableHead>
              <TableHead>操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {departments.map((department) => (
              <TableRow key={department.id}>
                <TableCell>{department.id}</TableCell>
                <TableCell>{department.name}</TableCell>
                <TableCell>{department.parent_id || '-'}</TableCell>
                <TableCell>{department.leader_id || '-'}</TableCell>
                <TableCell>{department.remark || '-'}</TableCell>
                <TableCell>{new Date(department.created_at).toLocaleString()}</TableCell>
                <TableCell>{new Date(department.updated_at).toLocaleString()}</TableCell>
                <TableCell>
                  <div className="space-x-2">
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(department)}>
                      编辑
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(department.id)}
                    >
                      删除
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <DepartmentForm
        open={isFormOpen}
        onOpenChange={handleFormClose}
        onSuccess={handleFormSuccess}
        initialData={currentDepartment}
        companyId={companyId}
      />
    </div>
  )
} 