import { AppLayout } from "@/components/layout/app-layout"

export default function PositionPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "职位管理", href: "/position" },
        { label: "职位列表" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        <h1>职位管理页面</h1>
      </div>
    </AppLayout>
  )
}
