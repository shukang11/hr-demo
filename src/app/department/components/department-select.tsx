import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { getDepartmentList } from "@/lib/api/department"
import { useEffect, useState } from "react"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

interface Department {
  id: number
  name: string
}

interface DepartmentSelectProps {
  value?: string
  onValueChange?: (value: string) => void
  companyId: number
  placeholder?: string
  excludeId?: number
}

export function DepartmentSelect({
  value,
  onValueChange,
  companyId,
  placeholder = "请选择部门",
  excludeId,
}: DepartmentSelectProps) {
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)

  // 获取当前选中部门的名称
  const selectedDepartmentName = departments.find(
    (dept) => dept.id.toString() === value
  )?.name

  useEffect(() => {
    const loadDepartments = async () => {
      try {
        setLoading(true)
        const result = await getDepartmentList(companyId, { page: 1, limit: 100 })
        // 过滤掉当前部门，避免自己选择自己作为上级部门
        const filteredDepartments = result.items
          .filter((dept) => !excludeId || dept.id !== excludeId)
          .map((dept) => ({
            id: dept.id,
            name: dept.name,
          }))
        setDepartments(filteredDepartments)

        // 如果当前选中的值不在列表中，清空它
        if (value && !filteredDepartments.some(dept => dept.id.toString() === value)) {
          onValueChange?.("")
        }
      } catch (error) {
        console.error("加载部门列表失败:", error)
      } finally {
        setLoading(false)
      }
    }

    if (companyId) {
      loadDepartments()
    }
  }, [companyId, excludeId, value, onValueChange])

  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger disabled={loading}>
        <SelectValue placeholder={loading ? "加载中..." : placeholder}>
          {loading ? (
            <LoadingSpinner className="mr-2 h-4 w-4" />
          ) : (
            selectedDepartmentName
          )}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {departments.map((department) => (
          <SelectItem key={department.id} value={department.id.toString()}>
            {department.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
} 