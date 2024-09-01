import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { Company } from '@/types';
import { dbGetAllCompanies, dbUpdateCompany } from '@/services/company';

interface CompanyContextProps {
  currentCompany: Company | null;
  changeCompany: (company: Company) => void;
}

const CompanyContext = createContext<CompanyContextProps | undefined>(undefined);

export const useCompany = () => {
  const context = useContext(CompanyContext);
  if (!context) {
    throw new Error('useCompany must be used within a CompanyProvider');
  }
  return context;
};

interface CompanyProviderProps {
  children: ReactNode;
}

export const CompanyProvider: React.FC<CompanyProviderProps> = ({ children }) => {
  const [currentCompany, setCurrentCompany] = useState<Company | null>(null);

  useEffect(() => {
    const loadCompany = async () => {
      const companies = await dbGetAllCompanies();
      if (companies.length > 0) {
        setCurrentCompany(companies[0]);
      }
    };
    loadCompany();
  }, []);

  const changeCompany = async (company: Company) => {
    await dbUpdateCompany(company);
    setCurrentCompany(company);
  };

  return (
    <CompanyContext.Provider value={{ currentCompany, changeCompany }}>
      {children}
    </CompanyContext.Provider>
  );
};