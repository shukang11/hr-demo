import { useState } from "react"
import useSWR from "swr"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table"
import { useToast } from "@/hooks/use-toast"
import { EmployeeForm } from "./employee-form"
import { EmployeePositionManager } from "./employee-position-manager"
import { Employee, deleteEmployee, getEmployeeList, searchEmployees } from "@/lib/api/employee"
import { useDebounce } from "@/hooks/use-debounce"
import { PageParams } from "@/lib/types"
import { useCompanyStore } from "@/hooks/use-company-store"

export function EmployeeList() {
  const { toast } = useToast()
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isPositionManagerOpen, setIsPositionManagerOpen] = useState(false)
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null)
  const [managingEmployee, setManagingEmployee] = useState<Employee | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const debouncedSearchTerm = useDebounce(searchTerm, 300)
  const { currentCompany } = useCompanyStore()
  
  const companyId = currentCompany?.id || 0;

  const [pageParams, setPageParams] = useState<PageParams>({
    page: 1,
    limit: 10,
  })

  const { data, error, mutate } = useSWR(
    ['employees', companyId, pageParams, debouncedSearchTerm],
    () => debouncedSearchTerm
      ? searchEmployees(companyId, debouncedSearchTerm, pageParams)
      : getEmployeeList(companyId, pageParams)
  )

  if (!currentCompany?.id) {
    return <div className="text-center text-muted-foreground">请先选择公司</div>
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteEmployee(id)
      toast({
        title: "删除成功",
        description: "员工信息已删除",
      })
      mutate()
    } catch (error) {
      toast({
        title: "删除失败",
        description: "无法删除员工信息",
        variant: "destructive",
      })
    }
  }

  const handleEdit = (employee: Employee) => {
    setEditingEmployee(employee)
    setIsFormOpen(true)
  }

  const handleManagePositions = (employee: Employee) => {
    setManagingEmployee(employee)
    setIsPositionManagerOpen(true)
  }

  const handleFormClose = (open: boolean) => {
    setIsFormOpen(open)
    if (!open) {
      setEditingEmployee(null)
    }
  }

  const handlePositionManagerClose = (open: boolean) => {
    setIsPositionManagerOpen(open)
    if (!open) {
      setManagingEmployee(null)
    }
  }

  const handleFormSuccess = () => {
    mutate()
    handleFormClose(false)
  }

  const isLoading = !data && !error

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex w-full max-w-sm items-center space-x-2">
          <Input
            placeholder="搜索员工..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <Button onClick={() => setIsFormOpen(true)}>添加员工</Button>
      </div>

      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>姓名</TableHead>
              <TableHead>邮箱</TableHead>
              <TableHead>电话</TableHead>
              <TableHead>性别</TableHead>
              <TableHead>地址</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center">
                  加载中...
                </TableCell>
              </TableRow>
            ) : error ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-destructive">
                  加载失败
                </TableCell>
              </TableRow>
            ) : data?.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center">
                  暂无数据
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((employee: Employee) => (
                <TableRow key={employee.id}>
                  <TableCell>{employee.name}</TableCell>
                  <TableCell>{employee.email || "-"}</TableCell>
                  <TableCell>{employee.phone || "-"}</TableCell>
                  <TableCell>
                    {employee.gender === "Male"
                      ? "男"
                      : employee.gender === "Female"
                      ? "女"
                      : "未知"}
                  </TableCell>
                  <TableCell>{employee.address || "-"}</TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleManagePositions(employee)}
                    >
                      管理职位
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(employee)}
                    >
                      编辑
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(employee.id)}
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

      <EmployeeForm
        open={isFormOpen}
        onOpenChange={handleFormClose}
        onSuccess={handleFormSuccess}
        initialData={editingEmployee}
        companyId={companyId}
      />

      {managingEmployee && (
        <EmployeePositionManager
          open={isPositionManagerOpen}
          onOpenChange={handlePositionManagerClose}
          employee={managingEmployee}
        />
      )}
    </div>
  )
}