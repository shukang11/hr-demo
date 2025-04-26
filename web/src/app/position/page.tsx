import  {AppLayout}  from "@/layout/app"
import { PositionList } from "./components/position-list"
import { useCompanyStore } from "@/hooks/use-company-store"

export default function PositionPage() {
  const { currentCompany } = useCompanyStore();

  return (
    <AppLayout
      breadcrumbs={[
        { label: "职位管理", href: "/position" },
        { label: "职位信息" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        {currentCompany?.id && <PositionList />}
        {!currentCompany?.id && <div className="text-center text-muted-foreground">请先选择公司</div>}
      </div>
    </AppLayout>
  )
}
