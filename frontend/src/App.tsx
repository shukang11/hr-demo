import { HashRouter, Routes, Route, Navigate } from "react-router-dom"

import { ThemeProvider } from "@/components/theme-provider"
import { Suspense, lazy } from "react"
import "./App.css"
import { ToastProvider } from "@/components/ui/toast"
import { Toaster } from "@/components/ui/toaster"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

// 懒加载导入所有页面组件
const DashboardPage = lazy(() => import("@/app/dashboard/page"))
const EmployeePage = lazy(() => import("@/app/employee/page"))
const DepartmentPage = lazy(() => import("@/app/department/page"))
const PositionPage = lazy(() => import("@/app/position/page"))
const CompanyPage = lazy(() => import("@/app/company/page"))
const AboutPage = lazy(() => import("@/app/about/page"))

// 创建加载包装组件
const PageWrapper = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<LoadingSpinner className="min-h-[400px]" />}>
    {children}
  </Suspense>
)

function App() {
  return (
    <HashRouter>
      <ThemeProvider>
        <ToastProvider>
          <div className="min-h-screen">
            <main>
              <Routes>
                {/* 默认重定向到仪表盘 */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                
                {/* 仪表盘路由 */}
                <Route 
                  path="/dashboard" 
                  element={
                    <PageWrapper>
                      <DashboardPage />
                    </PageWrapper>
                  } 
                />

                {/* 员工管理路由 */}
                <Route 
                  path="/employee" 
                  element={
                    <PageWrapper>
                      <EmployeePage />
                    </PageWrapper>
                  } 
                />

                {/* 部门管理路由 */}
                <Route 
                  path="/department" 
                  element={
                    <PageWrapper>
                      <DepartmentPage />
                    </PageWrapper>
                  } 
                />

                {/* 职位管理路由 */}
                <Route 
                  path="/position" 
                  element={
                    <PageWrapper>
                      <PositionPage />
                    </PageWrapper>
                  } 
                />

                {/* 公司管理路由 */}
                <Route 
                  path="/company" 
                  element={
                    <PageWrapper>
                      <CompanyPage />
                    </PageWrapper>
                  } 
                />

                {/* 关于页面路由 */}
                <Route 
                  path="/about" 
                  element={
                    <PageWrapper>
                      <AboutPage />
                    </PageWrapper>
                  } 
                />
              </Routes>
              <Toaster />
            </main>
          </div>
        </ToastProvider>
      </ThemeProvider>
    </HashRouter>
  )
}

export default App
