import { AppLayout } from "@/components/layout/app-layout"

export default function DepartmentPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "部门管理", href: "/department" },
        { label: "部门列表" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        <h1>部门管理页面</h1>
      </div>
    </AppLayout>
  )
}
