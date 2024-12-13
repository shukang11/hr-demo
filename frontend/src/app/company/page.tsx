import { AppLayout } from "@/components/layout/app-layout"

export default function CompanyPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "公司管理", href: "/company" },
        { label: "公司信息" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        <h1>公司管理页面</h1>
      </div>
    </AppLayout>
  )
}
