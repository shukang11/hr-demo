'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { open } from '@tauri-apps/plugin-dialog';
import {  BaseDirectory } from '@tauri-apps/plugin-fs';
import { useSetting } from '@/lib/providers/setting-provider';

const SettingsPage: React.FC = () => {
    const {setting, updateSetting} = useSetting();
  const [dataSourceUrl, setDataSourceUrl] = useState(setting.dataSourceUrl ?? "");
  const [defaultExportUrl, setDefaultExportUrl] = useState(setting.defaultExportUrl ?? "");
  const [backupUrl, setBackupUrl] = useState(setting.backupUrl ?? "");

  const handleSave = () => {
    console.log('数据源地址:', dataSourceUrl);
    console.log('默认导出地址:', defaultExportUrl);
    console.log('备份路径:', backupUrl);
    updateSetting({dataSourceUrl, defaultExportUrl, backupUrl});
  };

  const selectFolder = async (setter: React.Dispatch<React.SetStateAction<string>>) => {
    const selected = await open({
      directory: true,
      multiple: false,
      defaultPath: BaseDirectory.AppLocalData.toLocaleString()
    });
    
    if (Array.isArray(selected)) {
      // user selected multiple directories
    } else if (selected === null) {
      // user cancelled the selection
    } else {
      setter(selected as string);
      // user selected a single directory
    }
  };

  return (
    <div className="container mx-auto p-4">
      <div className="space-y-4">
        <div>
          <label htmlFor="dataSourceUrl" className="block text-sm font-medium text-gray-700">数据源地址</label>
          <div className="flex">
            <Input
              id="dataSourceUrl"
              type="text"
              value={dataSourceUrl}
              onChange={(e) => setDataSourceUrl(e.target.value)}
              className="mt-1 block w-full"
            />
            <Button onClick={() => selectFolder(setDataSourceUrl)} className="ml-2">导入</Button>
          </div>
        </div>
        <div>
          <label htmlFor="defaultExportUrl" className="block text-sm font-medium text-gray-700">默认导出地址</label>
          <div className="flex">
            <Input
              id="defaultExportUrl"
              type="text"
              value={defaultExportUrl}
              onChange={(e) => setDefaultExportUrl(e.target.value)}
              className="mt-1 block w-full"
            />
            <Button onClick={() => selectFolder(setDefaultExportUrl)} className="ml-2">导入</Button>
          </div>
        </div>
        <div>
          <label htmlFor="backupUrl" className="block text-sm font-medium text-gray-700">备份路径</label>
          <div className="flex">
            <Input
              id="backupUrl"
              type="text"
              value={backupUrl}
              onChange={(e) => setBackupUrl(e.target.value)}
              className="mt-1 block w-full"
            />
            <Button onClick={() => selectFolder(setBackupUrl)} className="ml-2">导入</Button>
          </div>
        </div>
        <Button onClick={handleSave} className="w-full">保存</Button>
      </div>
    </div>
  );
};

export default SettingsPage;

