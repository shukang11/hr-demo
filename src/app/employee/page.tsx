import { AppLayout } from "@/components/layout/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table"

export default function EmployeePage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "员工管理", href: "/employee" },
        { label: "员工列表" },
      ]}
    >
      <div className="h-full flex flex-col gap-4">
        {/* 搜索和操作区域 */}
        <div className="flex items-center justify-between">
          <div className="flex w-full max-w-sm items-center space-x-2">
            <Input placeholder="搜索员工..." />
          </div>
          <Button>添加员工</Button>
        </div>

        {/* 表格区域 */}
        <div className="flex-1 border rounded-lg bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>姓名</TableHead>
                <TableHead>部门</TableHead>
                <TableHead>职位</TableHead>
                <TableHead>入职日期</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {/* 示例数据 */}
              <TableRow>
                <TableCell>张三</TableCell>
                <TableCell>技术部</TableCell>
                <TableCell>前端工程师</TableCell>
                <TableCell>2024-01-01</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm">
                    编辑
                  </Button>
                </TableCell>
              </TableRow>
              {/* 可以添加更多行 */}
            </TableBody>
          </Table>
        </div>
      </div>
    </AppLayout>
  )
}
