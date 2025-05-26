'use client'

import { useState, useEffect } from 'react'
import { Check, ChevronsUpDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from '@/components/ui/command'
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'

interface SubsidiaryOption {
    id: number
    name: string
}

interface SubsidiarySelectorProps {
    parentCompany: SubsidiaryOption
    subsidiaries: SubsidiaryOption[]
    selectedIds: number[]
    onChange: (ids: number[]) => void
    className?: string
}

export function SubsidiarySelector({
    parentCompany,
    subsidiaries,
    selectedIds,
    onChange,
    className,
}: SubsidiarySelectorProps) {
    const [open, setOpen] = useState(false)
    const allOptions = [parentCompany, ...subsidiaries]

    // 计算选中的数量
    const selectedCount = selectedIds.length
    const totalCount = allOptions.length

    // 查找选中的公司名称
    const getSelectedNames = () => {
        return allOptions
            .filter(option => selectedIds.includes(option.id))
            .map(option => option.name)
    }

    // 切换选择状态
    const toggleOption = (id: number) => {
        if (selectedIds.includes(id)) {
            onChange(selectedIds.filter(i => i !== id))
        } else {
            onChange([...selectedIds, id])
        }
    }

    // 全选/取消全选
    const toggleAll = () => {
        if (selectedIds.length === allOptions.length) {
            onChange([])
        } else {
            onChange(allOptions.map(option => option.id))
        }
    }

    return (
        <div className={className}>
            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        className="justify-between w-full max-w-md"
                    >
                        {selectedCount > 0 ? (
                            <span className="flex items-center gap-1 truncate">
                                已选择
                                <Badge variant="secondary" className="ml-1">
                                    {selectedCount}/{totalCount}
                                </Badge>
                                {selectedCount <= 2 && (
                                    <span className="ml-1 truncate">
                                        {getSelectedNames().join('、')}
                                    </span>
                                )}
                            </span>
                        ) : (
                            "选择公司"
                        )}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full max-w-md p-0">
                    <Command>
                        <CommandInput placeholder="搜索公司..." />
                        <CommandList>
                            <CommandEmpty>未找到公司</CommandEmpty>
                            <CommandGroup>
                                <CommandItem
                                    onSelect={toggleAll}
                                    className="flex items-center gap-2 cursor-pointer"
                                >
                                    <Checkbox
                                        checked={selectedIds.length === allOptions.length}
                                        className="data-[state=checked]:bg-primary"
                                    />
                                    <span>全选</span>
                                </CommandItem>

                                {allOptions.map((option) => (
                                    <CommandItem
                                        key={option.id}
                                        onSelect={() => toggleOption(option.id)}
                                        className="flex items-center gap-2 cursor-pointer"
                                    >
                                        <Checkbox
                                            checked={selectedIds.includes(option.id)}
                                            className="data-[state=checked]:bg-primary"
                                        />
                                        <span>{option.name}</span>
                                        {option.id === parentCompany.id && (
                                            <Badge variant="outline" className="ml-auto">母公司</Badge>
                                        )}
                                    </CommandItem>
                                ))}
                            </CommandGroup>
                        </CommandList>
                    </Command>
                </PopoverContent>
            </Popover>
        </div>
    )
}
