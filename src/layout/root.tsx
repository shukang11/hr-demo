import { Outlet } from "react-router-dom"


export default function RootLayout() {

  return (
    <div className="min-h-screen">
      {/* 顶部导航栏 */}
      

      {/* 主要内容区域 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  )
} 