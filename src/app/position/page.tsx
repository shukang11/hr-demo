import  {AppLayout}  from "@/layout/app"
import { PositionList } from "./components/position-list"

export default function PositionPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "职位管理", href: "/position" },
        { label: "职位信息" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        <PositionList />
      </div>
    </AppLayout>
  )
}
