import { AppLayout } from "@/components/layout/app-layout"
import { EmployeeList } from "./components/employee-list"

export default function EmployeePage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "员工管理", href: "/employee" },
        { label: "员工信息" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        <EmployeeList />
      </div>
    </AppLayout>
  )
}
