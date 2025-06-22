import { Outlet, useLocation } from "react-router-dom"
import { AppLayout, AppLayoutProps } from "./app"

// 路由面包屑映射
const BREADCRUMB_MAP: Record<string, string> = {
  dashboard: "看板",
  candidate: "候选人",
  employee: "员工",
  department: "部门",
  position: "职位",
  company: "公司",
  about: "关于",
}

export default function RootLayout() {
  const breadcrumbs: AppLayoutProps["breadcrumbs"] = [
  ]

  return (
    <AppLayout breadcrumbs={breadcrumbs}>
      <Outlet />
    </AppLayout>
  )
} 