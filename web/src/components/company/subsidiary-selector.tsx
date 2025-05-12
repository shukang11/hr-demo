import { useEffect, useState } from "react";
import { Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
    useCompanySubsidiaries,
    useCompanyName
} from "@/lib/api/company";
import { Skeleton } from "@/components/ui/skeleton";

interface SubsidiarySelectorProps {
    parentId: number;
    selectedIds: number[];
    onChange: (selectedIds: number[]) => void;
    includeParent?: boolean;
}

interface SubsidiaryOption {
    id: number;
    name: string;
}

export function SubsidiarySelector({
    parentId,
    selectedIds,
    onChange,
    includeParent = true,
}: SubsidiarySelectorProps) {
    const [open, setOpen] = useState(false);
    const [options, setOptions] = useState<SubsidiaryOption[]>([]);
    const { data: subsidiaries, isLoading: isLoadingSubsidiaries } = useCompanySubsidiaries(parentId);
    const { data: parentCompany, isLoading: isLoadingParent } = useCompanyName(parentId);

    // 构建选项列表，包括父公司（如果需要）和所有子公司
    useEffect(() => {
        const allOptions: SubsidiaryOption[] = [];

        // 添加父公司
        if (includeParent && parentCompany) {
            allOptions.push({
                id: parentId,
                name: `${parentCompany} (母公司)`,
            });
        }

        // 添加所有子公司
        if (subsidiaries) {
            subsidiaries.forEach(sub => {
                allOptions.push({
                    id: sub.id,
                    name: sub.name,
                });
            });
        }

        setOptions(allOptions);
    }, [parentId, subsidiaries, parentCompany, includeParent]);

    // 切换选择状态
    const toggleSelection = (id: number) => {
        if (selectedIds.includes(id)) {
            onChange(selectedIds.filter(i => i !== id));
        } else {
            onChange([...selectedIds, id]);
        }
    };

    // 全选
    const selectAll = () => {
        onChange(options.map(option => option.id));
    };

    // 全不选
    const selectNone = () => {
        onChange([]);
    };

    // 获取已选择公司的名称列表
    const getSelectedNames = () => {
        return options
            .filter(option => selectedIds.includes(option.id))
            .map(option => option.name);
    };

    return (
        <div className="space-y-2">
            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        className="w-full justify-between"
                    >
                        {selectedIds.length > 0
                            ? `已选择 ${selectedIds.length} 家公司`
                            : "选择公司"}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0">
                    {(isLoadingSubsidiaries || isLoadingParent) ? (
                        <div className="p-4 space-y-2">
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-3/4" />
                            <Skeleton className="h-4 w-1/2" />
                        </div>
                    ) : (
                        <Command>
                            <CommandInput placeholder="搜索公司..." />
                            <CommandList>
                                <CommandEmpty>未找到匹配的公司</CommandEmpty>
                                <CommandGroup>
                                    <CommandItem
                                        onSelect={selectAll}
                                        className="cursor-pointer"
                                    >
                                        <div className="flex items-center gap-2 w-full">
                                            <Checkbox
                                                checked={selectedIds.length === options.length && options.length > 0}
                                            />
                                            <span>选择全部</span>
                                        </div>
                                    </CommandItem>
                                    <CommandItem
                                        onSelect={selectNone}
                                        className="cursor-pointer"
                                    >
                                        <div className="flex items-center gap-2 w-full">
                                            <Checkbox checked={selectedIds.length === 0} />
                                            <span>取消全部</span>
                                        </div>
                                    </CommandItem>
                                    {options.map((option) => (
                                        <CommandItem
                                            key={option.id}
                                            onSelect={() => toggleSelection(option.id)}
                                            className="cursor-pointer"
                                        >
                                            <div className="flex items-center gap-2 w-full">
                                                <Checkbox checked={selectedIds.includes(option.id)} />
                                                <span>{option.name}</span>
                                            </div>
                                        </CommandItem>
                                    ))}
                                </CommandGroup>
                            </CommandList>
                        </Command>
                    )}
                </PopoverContent>
            </Popover>

            {/* 显示已选择的公司标签 */}
            <div className="flex flex-wrap gap-2">
                {getSelectedNames().map((name, index) => (
                    <Badge key={index} variant="secondary">
                        {name}
                    </Badge>
                ))}
            </div>
        </div>
    );
}
