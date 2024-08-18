import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { SettingProviderValue } from '@/types/settings';
import { mkdir, exists, BaseDirectory } from '@tauri-apps/plugin-fs';
import { Store } from "@tauri-apps/plugin-store";



interface SettingContextProps {
  setting: SettingProviderValue;
  updateSetting: (newSetting: Partial<SettingProviderValue>) => void;
}

const SettingContext = createContext<SettingContextProps | undefined>(undefined);

export const useSetting = () => {
  const context = useContext(SettingContext);
  if (!context) {
    throw new Error('useSetting must be used within a SettingProvider');
  }
  return context;
};

interface SettingProviderProps {
  children: ReactNode;
  initialSetting?: SettingProviderValue;
}

export const SettingProvider: React.FC<SettingProviderProps> = ({ children, initialSetting = {} as SettingProviderValue }) => {

  const [setting, setSetting] = useState<SettingProviderValue>(initialSetting);
  const settingPath = `.setting.dat`;
  const store = new Store(settingPath);
  const settingKey = "root";

  useEffect(() => {
    const loadSetting = async () => {
      await store.load();

      const setting = await store.get<SettingProviderValue>(settingKey);
      if (!setting) {
        return;
      }
      setSetting(setting);
    };
    loadSetting();
  }, []);


  const updateSetting = async (newSetting: Partial<SettingProviderValue>) => {

    setSetting((prevSetting) => ({ ...prevSetting, ...newSetting }));

    await store.load();

    await store.set(settingKey, { ...setting, ...newSetting });

    await store.save();
  };

  return (
    <SettingContext.Provider value={{ setting, updateSetting }}>
      {children}
    </SettingContext.Provider>
  );
};
