import { Outlet, Link, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"

const navigation = [
  { name: '仪表盘', href: '/dashboard' },
  { name: '员工管理', href: '/employee' },
  { name: '部门管理', href: '/department' },
  { name: '职位管理', href: '/position' },
  { name: '公司管理', href: '/company' },
  { name: '关于', href: '/about' },
]

export default function RootLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/auth/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              {/* Logo */}
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold">HR System</span>
              </div>
              {/* 导航链接 */}
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navigation.map((item) => (
                  <Link
                    key={item.href}
                    to={item.href}
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900"
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
            {/* 右侧按钮 */}
            <div className="flex items-center">
              <Button
                variant="ghost"
                onClick={handleLogout}
              >
                退出登录
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* 主要内容区域 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  )
} 