import { create } from 'zustand'
import type { Company } from '@/lib/api/company'

interface CompanyState {
  currentCompany: Company | null
}

interface CompanyActions {
  setCurrentCompany: (company: Company | null) => void
}

type CompanyStore = CompanyState & CompanyActions

export const useCompanyStore = create<CompanyStore>((set) => ({
  currentCompany: null,
  setCurrentCompany: (company) => set(() => ({ currentCompany: company })),
})) 