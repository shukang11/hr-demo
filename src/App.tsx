import { HashRouter, Routes, Route, Navigate } from "react-router-dom"
import { ThemeProvider } from "@/components/theme-provider"
import { Suspense, lazy } from "react"
import "./App.css"
import { Toaster } from "@/components/ui/toaster"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

// 布局组件
import AuthLayout from "@/layout/auth"
import RootLayout from "@/layout/root"

// 懒加载导入所有功能页面组件
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
    <div className="w-full min-h-screen">
      <HashRouter>
        <ThemeProvider>
          <Routes>
            {/* 功能页面路由 */}
            <Route
              path="/"
              element={
                <RootLayout />
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route
                path="dashboard"
                element={
                  <PageWrapper>
                    <DashboardPage />
                  </PageWrapper>
                }
              />
              <Route
                path="employee"
                element={
                  <PageWrapper>
                    <EmployeePage />
                  </PageWrapper>
                }
              />
              <Route
                path="department"
                element={
                  <PageWrapper>
                    <DepartmentPage />
                  </PageWrapper>
                }
              />
              <Route
                path="position"
                element={
                  <PageWrapper>
                    <PositionPage />
                  </PageWrapper>
                }
              />
              <Route
                path="company"
                element={
                  <PageWrapper>
                    <CompanyPage />
                  </PageWrapper>
                }
              />
              <Route
                path="about"
                element={
                  <PageWrapper>
                    <AboutPage />
                  </PageWrapper>
                }
              />
            </Route>
          </Routes>
          <Toaster />
        </ThemeProvider>
      </HashRouter>
    </div>
  )
}

export default App
