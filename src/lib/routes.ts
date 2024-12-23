import {
  LayoutDashboard,
  Users,
  Building2,
  Briefcase,
  Building,
  Info
} from "lucide-react"
import { LucideIcon } from "lucide-react"

export interface Route {
  path: string
  label: string
  icon: LucideIcon
  children?: Route[]
}

export const routes: Route[] = [
  {
    path: '/dashboard',
    label: '仪表盘',
    icon: LayoutDashboard
  },
  {
    path: '/candidate',
    label: '候选人管理',
    icon: Users
  },
  {
    path: '/employee',
    label: '员工管理',
    icon: Users
  },
  {
    path: '/department',
    label: '部门管理',
    icon: Building2
  },
  {
    path: '/position',
    label: '职位管理',
    icon: Briefcase
  },
  {
    path: '/company',
    label: '公司管理',
    icon: Building
  },
  {
    path: '/about',
    label: '关于我们',
    icon: Info
  },
]