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

export function AppSidebar({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  const location = useLocation()
  const { currentCompany, setCurrentCompany } = useCompanyStore()
  const { data: companyData } = useCompanies({ page: 1, limit: 100 } as PageParams)

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
    </aside>
  )
}
