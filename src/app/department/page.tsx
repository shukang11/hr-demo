import { DepartmentList } from "./components/department-list"
import { AppLayout } from "@/components/layout/app-layout"

export default function DepartmentPage() {
  // TODO: 这里需要从路由或者其他地方获取公司ID
  const companyId = 1

  return (
    <AppLayout
      breadcrumbs={[
        { label: "部门管理", href: "/department" },
        { label: "部门列表" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        <DepartmentList companyId={companyId} />
      </div>
    </AppLayout>
  )
}
