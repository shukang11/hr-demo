import  {AppLayout}  from "@/layout/app"
import { EmployeeList } from "./components/employee-list"
import { useCompanyStore } from "@/hooks/use-company-store"

export default function EmployeePage() {
  const { currentCompany } = useCompanyStore();

  return (
    <AppLayout
      breadcrumbs={[
        { label: "员工管理", href: "/employee" },
        { label: "员工信息" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        {currentCompany?.id && <EmployeeList />}
        {!currentCompany?.id && <div className="text-center text-muted-foreground">请先选择公司</div>}
      </div>
    </AppLayout>
  )
}
