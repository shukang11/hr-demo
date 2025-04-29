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

    useEffect(() => {
        if (!isAuthenticated && !loading) {
            checkAuth();
        }
    }, [isAuthenticated, checkAuth, loading]);

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