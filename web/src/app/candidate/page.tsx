import { AppLayout } from "@/layout/app"
import { CandidateList } from "./components/candidate-list.tsx"
import { useCompanyStore } from "@/hooks/use-company-store"

export default function CandidatePage() {
  const { currentCompany } = useCompanyStore();

  return (
    <AppLayout
      breadcrumbs={[
        { label: "候选人管理", href: "/candidate" },
        { label: "候选人信息" },
      ]}
    >
      <div className="rounded-xl bg-muted/50 p-4">
        {currentCompany?.id && <CandidateList />}
        {!currentCompany?.id && <div className="text-center text-muted-foreground">请先选择公司</div>}
      </div>
    </AppLayout>
  )
} 