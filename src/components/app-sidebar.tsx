import { cn } from "@/lib/utils"
import { routes } from "@/lib/routes"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useLocation, Link } from "react-router-dom"
import type { HTMLAttributes } from "react"
import { useCompanyStore } from "@/hooks/use-company-store"
import { useCompanies } from "@/lib/api/company"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { PageParams } from "@/lib/types"
import { useAuth } from "@/lib/auth/auth-context"
import { LogOut, User } from "lucide-react"
import { Avatar, AvatarFallback } from "./ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "./ui/dropdown-menu"
import { useToast } from "@/hooks/use-toast"

export function AppSidebar({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  const location = useLocation()
  const { user, logout } = useAuth()
  const { toast } = useToast()
  const { currentCompany, setCurrentCompany } = useCompanyStore()
  const { data: companyData } = useCompanies({ page: 1, limit: 100 } as PageParams)

  // 获取用户名首字母作为头像
  const getInitials = (name: string = '') => {
    return name.charAt(0).toUpperCase();
  };

  // 处理登出操作
  const handleLogout = async () => {
    try {
      await logout();
      toast({
        title: "登出成功",
        description: "您已成功退出系统"
      });
    } catch (error) {
      console.error("登出失败", error);
      toast({
        variant: "destructive",
        title: "登出失败",
        description: "请稍后重试"
      });
    }
  };

  return (
    <aside className={cn("flex flex-col", className)} {...props}>
      <div className="flex h-14 items-center border-b px-4">
        <div className="flex flex-col gap-1 w-full">
          <Select
            value={currentCompany?.id?.toString()}
            onValueChange={(value) => {
              const company = companyData?.items.find(
                (item) => item.id.toString() === value
              )
              setCurrentCompany(company || null)
            }}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="选择公司" />
            </SelectTrigger>
            <SelectContent>
              {companyData?.items.map((company) => (
                <SelectItem key={company.id} value={company.id.toString()}>
                  {company.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <ScrollArea className="flex-1 px-4">
        <nav className="grid gap-1 py-4">
          {routes.map((route, index) => {
            const Icon = route.icon
            const isActive = location.pathname === route.path
            return (
              <Button
                key={index}
                asChild
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start",
                  isActive && "bg-secondary font-medium"
                )}
              >
                <Link to={route.path}>
                  <Icon className="mr-2 h-4 w-4" />
                  {route.label}
                </Link>
              </Button>
            )
          })}
        </nav>
      </ScrollArea>

      {/* 用户信息和登出区域 */}
      <div className="mt-auto border-t p-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="w-full justify-start p-2">
              <Avatar className="h-8 w-8 mr-2">
                <AvatarFallback>{getInitials(user?.username)}</AvatarFallback>
              </Avatar>
              <div className="flex flex-col items-start text-sm">
                <span className="font-medium">{user?.username || '未登录'}</span>
                <span className="text-xs text-muted-foreground truncate max-w-[120px]">
                  {user?.email || ''}
                </span>
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>我的账户</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="cursor-pointer">
              <User className="mr-2 h-4 w-4" />
              <span>个人资料</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
              <LogOut className="mr-2 h-4 w-4" />
              <span>退出登录</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  )
}
