import { ThemeProvider } from "@/components/theme-provider"
import { CardProvider } from "@/pages/excel-2-card/card-context"
import { type ReactNode } from "react"

interface ProvidersProps {
  children: ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider>
      <CardProvider>
        {children}
      </CardProvider>
    </ThemeProvider>
  )
} 