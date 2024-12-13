import { cn } from "@/lib/utils"
import { routes } from "@/lib/routes"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useLocation, Link } from "react-router-dom"
import type { HTMLAttributes } from "react"

export function AppSidebar({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  const location = useLocation()

  return (
    <aside className={cn("flex flex-col", className)} {...props}>
      <div className="flex h-14 items-center border-b px-6">
        <Link to="/" className="flex items-center space-x-2">
          <span className="h-6 w-6 rounded-lg bg-primary" />
          <span className="font-semibold">Acme Inc</span>
        </Link>
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
