import React from "react"

interface AuthLayoutProps {
  children: React.ReactNode
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-background to-muted/50 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md bg-card shadow-lg rounded-xl border overflow-hidden">
        {children}
      </div>
      <div className="mt-8 text-center text-muted-foreground text-xs">
        © {new Date().getFullYear()} HR管理系统 | 安全登录
      </div>
    </div>
  )
}