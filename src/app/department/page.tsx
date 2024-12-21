import { useCompanyStore } from "@/hooks/use-company-store"
import { DepartmentList } from "./components/department-list"
import  {AppLayout}  from "@/layout/app"

export default function DepartmentPage() {

  const { currentCompany } = useCompanyStore()

  return (
    <AppLayout
      breadcrumbs={[
        { label: "部门管理", href: "/department" },
        { label: "部门列表" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        {currentCompany?.id && <DepartmentList companyId={currentCompany?.id} />}
        {!currentCompany?.id && <div className="text-center text-muted-foreground">请先选择公司</div>}
      </div>
    </AppLayout>
  )
}
