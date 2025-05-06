/**
 * JSON Schema选择器组件
 * 
 * 允许用户从可用的Schema列表中选择一个Schema应用到实体。
 */
import { useState, useEffect } from "react";
import {
    JsonSchemaSchema,
    useSchemaList
} from "@/lib/api/customfield";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Loader2, Plus } from "lucide-react";

export interface SchemaSelectorProps {
    /**
     * 实体类型，如"Company"、"Employee"等
     */
    entityType: string;

    /**
     * 当前选中的Schema ID
     */
    value?: number | null;

    /**
     * 选择变更回调函数
     */
    onChange?: (schemaId: number | null) => void;

    /**
     * 公司ID，用于筛选该公司的Schema
     */
    companyId?: number;

    /**
     * 是否包含系统Schema，默认为true
     */
    includeSystem?: boolean;

    /**
     * 创建新Schema的回调函数
     */
    onCreateNew?: () => void;

    /**
     * 是否显示创建新Schema按钮，默认为true
     */
    showCreateButton?: boolean;

    /**
     * 是否禁用选择器，默认为false
     */
    disabled?: boolean;
}

/**
 * Schema选择器组件
 * 
 * 从可用的Schema列表中选择一个Schema。
 * 
 * @example
 * ```tsx
 * <SchemaSelector 
 *   entityType="Company"
 *   value={selectedSchemaId}
 *   onChange={setSelectedSchemaId}
 *   companyId={currentCompanyId}
 * />
 * ```
 */
export function SchemaSelector({
    entityType,
    value,
    onChange,
    companyId,
    includeSystem = true,
    onCreateNew,
    showCreateButton = true,
    disabled = false,
}: SchemaSelectorProps) {
    // 获取Schema列表
    const { data, error, isLoading } = useSchemaList(
        entityType,
        { page: 1, limit: 100 },
        companyId,
        includeSystem
    );

    // 处理选择变更
    const handleChange = (value: string) => {
        const schemaId = value ? parseInt(value) : null;
        onChange?.(schemaId);
    };

    // 获取Schema列表
    const schemas = data?.data || [];

    return (
        <div className="flex items-center gap-2">
            <Select
                value={value?.toString() || ""}
                onValueChange={handleChange}
                disabled={disabled || isLoading}
            >
                <SelectTrigger className="w-full">
                    {isLoading ? (
                        <div className="flex items-center">
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            <span>加载中...</span>
                        </div>
                    ) : (
                        <SelectValue placeholder="选择自定义字段模板" />
                    )}
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="">无</SelectItem>
                    {schemas.map((schema) => (
                        <SelectItem key={schema.id} value={schema.id.toString()}>
                            {schema.name}
                            {schema.is_system && " (系统)"}
                            {schema.company_id && schema.company_id !== companyId && " (外部)"}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>

            {showCreateButton && onCreateNew && (
                <Button
                    size="icon"
                    variant="outline"
                    onClick={() => onCreateNew()}
                    disabled={disabled}
                    title="创建新模板"
                >
                    <Plus className="h-4 w-4" />
                </Button>
            )}
        </div>
    );
}