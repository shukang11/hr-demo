import { useEffect } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./auth-context";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { isAuthenticated, loading, checkAuth } = useAuth();
    const location = useLocation();

    // 修复：只在初次加载和非认证状态下检查认证，避免无限循环
    useEffect(() => {
        // 只有当用户未认证且不在加载状态时，才检查认证状态
        if (!isAuthenticated && !loading) {
            // 使用立即执行的异步函数包装checkAuth调用
            const verifyAuth = async () => {
                await checkAuth();
            };
            verifyAuth();
        }
    }, [/* 移除依赖项，只在组件挂载时执行一次 */]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <LoadingSpinner className="w-12 h-12" />
            </div>
        );
    }

    if (!isAuthenticated) {
        // 保存当前路径，以便登录后重定向回来
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <>{children}</>;
}