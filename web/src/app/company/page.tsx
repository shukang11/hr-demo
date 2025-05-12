import { AppLayout } from "@/layout/app"
import { CompanyList } from "./components/company-list"

export default function CompanyPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "公司管理", href: "/company" },
        { label: "公司信息" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        <CompanyList />
      </div>
    </AppLayout>
  )
}
