import { HashRouter, Routes, Route, Navigate } from "react-router-dom"
import { ThemeProvider } from "@/components/theme-provider"
import { Suspense, lazy } from "react"
import "./App.css"
import { Toaster } from "@/components/ui/toaster"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

import RootLayout from "@/layout/root"
import AuthLayout from "@/layout/auth"
import { AuthProvider } from "./lib/auth/auth-context"
import { ProtectedRoute } from "./lib/auth/protected-route"

// 懒加载导入所有功能页面组件
const DashboardPage = lazy(() => import("@/app/dashboard/page"))
const GroupDashboardPage = lazy(() => import("@/app/dashboard/group-view/page"))
const CandidatePage = lazy(() => import("@/app/candidate/page"))
const EmployeePage = lazy(() => import("@/app/employee/page"))
const DepartmentPage = lazy(() => import("@/app/department/page"))
const PositionPage = lazy(() => import("@/app/position/page"))
const CompanyPage = lazy(() => import("@/app/company/page"))
const CompanyDetailPage = lazy(() => import("@/app/company/detail/page"))
const AboutPage = lazy(() => import("@/app/about/page"))
const LoginPage = lazy(() => import("@/app/auth/login/page"))
const CustomFieldPage = lazy(() => import("@/app/customfield/page"))

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
          <AuthProvider>
            <Routes>
              {/* 认证相关路由 */}
              <Route
                path="/login"
                element={
                  <AuthLayout>
                    <PageWrapper>
                      <LoginPage />
                    </PageWrapper>
                  </AuthLayout>
                }
              />

              {/* 功能页面路由 */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <RootLayout />
                  </ProtectedRoute>
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
                  path="dashboard/group-view/:parentId"
                  element={
                    <PageWrapper>
                      <GroupDashboardPage />
                    </PageWrapper>
                  }
                />
                <Route
                  path="candidate"
                  element={
                    <PageWrapper>
                      <CandidatePage />
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
                  path="company/:id"
                  element={
                    <PageWrapper>
                      <CompanyDetailPage />
                    </PageWrapper>
                  }
                />
                <Route
                  path="customfield"
                  element={
                    <PageWrapper>
                      <CustomFieldPage />
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

              {/* 捕获所有其他路由，重定向到首页 */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
      </HashRouter>
    </div>
  )
}

export default App
