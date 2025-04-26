import { create } from 'zustand'
import type { Company } from '@/lib/api/company'

const STORAGE_KEY = 'app-current-company'

interface CompanyState {
  currentCompany: Company | null
}

interface CompanyActions {
  setCurrentCompany: (company: Company | null) => void
}

type CompanyStore = CompanyState & CompanyActions

// 从 localStorage 获取初始数据
const getInitialState = (): CompanyState => {
  if (typeof window === 'undefined') return { currentCompany: null }
  
  try {
    const storedData = localStorage.getItem(STORAGE_KEY)
    if (!storedData) return { currentCompany: null }
    
    return { currentCompany: JSON.parse(storedData) }
  } catch (error) {
    console.error('Failed to parse stored company data:', error)
    return { currentCompany: null }
  }
}

export const useCompanyStore = create<CompanyStore>((set) => ({
  ...getInitialState(),
  setCurrentCompany: (company) => {
    if (typeof window !== 'undefined') {
      if (company) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(company))
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }
    }
    set(() => ({ currentCompany: company }))
  },
})) 