import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { getEmployeeList } from "@/lib/api/employee"
import { useEffect, useState } from "react"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

interface Employee {
  id: number
  name: string
}

interface EmployeeSelectProps {
  value?: string
  onValueChange?: (value: string) => void
  companyId: number
  placeholder?: string
}

export function EmployeeSelect({
  value,
  onValueChange,
  companyId,
  placeholder = "请选择员工",
}: EmployeeSelectProps) {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)

  // 获取当前选中员工的名称
  const selectedEmployeeName = employees.find(
    (emp) => emp.id.toString() === value
  )?.name

  useEffect(() => {
    const loadEmployees = async () => {
      try {
        setLoading(true)
        const result = await getEmployeeList(companyId, { page: 1, limit: 100 })
        const employeeList = result.items.map((emp) => ({
          id: emp.id,
          name: emp.name,
        }))
        setEmployees(employeeList)

        // 如果当前选中的值不在列表中，清空它
        if (value && !employeeList.some(emp => emp.id.toString() === value)) {
          onValueChange?.("")
        }
      } catch (error) {
        console.error("加载员工列表失败:", error)
      } finally {
        setLoading(false)
      }
    }

    if (companyId) {
      loadEmployees()
    }
  }, [companyId, value, onValueChange])

  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger disabled={loading}>
        <SelectValue placeholder={loading ? "加载中..." : placeholder}>
          {loading ? (
            <LoadingSpinner className="mr-2 h-4 w-4" />
          ) : (
            selectedEmployeeName
          )}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {employees.map((employee) => (
          <SelectItem key={employee.id} value={employee.id.toString()}>
            {employee.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
} 