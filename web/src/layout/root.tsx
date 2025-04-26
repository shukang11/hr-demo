import { Outlet, useLocation } from "react-router-dom"
import { AppLayout } from "./app"

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
  const location = useLocation()
  const path = location.pathname.split("/")[1] || "dashboard"
  const breadcrumbs = [
    { label: "首页", href: "/" },
    { label: BREADCRUMB_MAP[path] || path },
  ]

  return (
    <AppLayout breadcrumbs={breadcrumbs}>
      <Outlet />
    </AppLayout>
  )
} 