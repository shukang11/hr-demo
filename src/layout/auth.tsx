import { Outlet } from "react-router-dom"

export default function AuthLayout() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gray-50 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-[480px] bg-white shadow-lg rounded-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">HR 管理系统</h1>
          <p className="mt-2 text-gray-600">请登录或注册以继续</p>
        </div>
        <div className="w-full">
          <Outlet />
        </div>
      </div>
    </div>
  )
} 