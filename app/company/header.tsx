'use client';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import React, { useState } from 'react';

interface CompanyHeaderProps {
  companyName: string;
  onEdit: (newName: string) => void;
}

const CompanyHeader: React.FC<CompanyHeaderProps> = ({ companyName, onEdit }) => {
  const [open, setOpen] = useState(false);
  const [newName, setNewName] = useState(companyName);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleSave = () => {
    onEdit(newName);
    handleClose();
  };

  return (
    <div>
      <div>
        <span>{companyName}</span>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button onClick={handleClickOpen}>编辑</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>编辑公司名</DialogTitle>
              <DialogDescription>
                请输入新的公司名。
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <Input
                id="name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="col-span-3"
              />
            </div>
            <DialogFooter>
              <Button type="submit" onClick={handleSave}>保存</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default CompanyHeader;
