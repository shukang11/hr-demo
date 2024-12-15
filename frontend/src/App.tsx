import { HashRouter, Routes, Route, Navigate } from "react-router-dom"
import { ThemeProvider } from "@/components/theme-provider"
import { Suspense, lazy } from "react"
import "./App.css"
import { ToastProvider } from "@/components/ui/toast"
import { Toaster } from "@/components/ui/toaster"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

// 布局组件
import AuthLayout from "@/layout/auth"
import RootLayout from "@/layout/root"

// 认证页面
import LoginPage from '@/app/auth/login/page'
import RegisterPage from '@/app/auth/register/page'

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

// 路由保护组件
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/auth/login" replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <div className="w-full min-h-screen">
      <HashRouter>
        <ThemeProvider>
          <ToastProvider>
            <Routes>
              {/* 认证相关路由 */}
              <Route path="/auth" element={<AuthLayout />}>
                <Route path="login" element={<LoginPage />} />
                <Route path="register" element={<RegisterPage />} />
              </Route>

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
          </ToastProvider>
        </ThemeProvider>
      </HashRouter>
    </div>
  );
}

export default App;
