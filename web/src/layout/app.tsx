import * as React from "react"
import { AppSidebar } from "@/components/app-sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Button } from "@/components/ui/button"
import {
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "@/components/theme-provider"

interface AppLayoutProps {
  children: React.ReactNode
  breadcrumbs: {
    label: string
    href?: string
  }[]
}

export function AppLayout({ children, breadcrumbs }: AppLayoutProps) {
  const { theme, setTheme } = useTheme()

  return (
    <div className="fixed inset-0 flex">
      <SidebarProvider defaultOpen={true}>
        <div className="flex min-h-screen w-screen">
          <AppSidebar className="w-64 shrink-0 border-r" />
          <div className="flex w-full flex-col">
            <header className="flex h-14 items-center justify-between border-b px-6">
              <div className="flex items-center gap-4">
                <SidebarTrigger className="lg:hidden" />
                <Breadcrumb>
                  <BreadcrumbList>
                    {breadcrumbs.map((item, index) => (
                      <React.Fragment key={index}>
                        <BreadcrumbItem>
                          {item.href ? (
                            <BreadcrumbLink 
                              href={item.href}
                              className="text-sm font-medium text-muted-foreground hover:text-foreground"
                            >
                              {item.label}
                            </BreadcrumbLink>
                          ) : (
                            <BreadcrumbPage className="text-sm font-medium">
                              {item.label}
                            </BreadcrumbPage>
                          )}
                        </BreadcrumbItem>
                        {index < breadcrumbs.length - 1 && <BreadcrumbSeparator />}
                      </React.Fragment>
                    ))}
                  </BreadcrumbList>
                </Breadcrumb>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setTheme(theme === "light" ? "dark" : "light")}
                className="h-9 w-9"
              >
                <Sun className="h-4 w-4 rotate-0 scale-100 transition-transform dark:-rotate-90 dark:scale-0" />
                <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-transform dark:rotate-0 dark:scale-100" />
                <span className="sr-only">Toggle theme</span>
              </Button>
            </header>
            <main className="flex-1 overflow-y-auto">
              <div className="mx-auto h-full w-full max-w-[1600px] p-6">
                {children}
              </div>
            </main>
          </div>
        </div>
      </SidebarProvider>
    </div>
  )
} 