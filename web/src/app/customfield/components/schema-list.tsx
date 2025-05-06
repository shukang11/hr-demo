/**
 * Schema列表组件
 * 
 * 展示所有可用的自定义字段模板，支持按实体类型筛选。
 */
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Copy, PencilIcon, Plus, Trash2 } from "lucide-react";
import {
    JsonSchemaSchema,
    deleteJsonSchema,
    useSchemaList,
} from "@/lib/api/customfield";
import { PageParams } from "@/lib/types";
import { Card } from "@/components/ui/card";

interface SchemaListProps {
    /**
     * 选中Schema时的回调
     */
    onSelectSchema?: (schema: JsonSchemaSchema) => void;

    /**
     * 创建新Schema时的回调
     */
    onCreateSchema?: (entityType: string) => void;

    /**
     * 编辑Schema时的回调
     */
    onEditSchema?: (schema: JsonSchemaSchema) => void;

    /**
     * 克隆Schema时的回调
     */
    onCloneSchema?: (schema: JsonSchemaSchema) => void;
}

const ENTITY_TYPE_OPTIONS = [
    { value: "all", label: "全部" },
    { value: "Company", label: "公司" },
    { value: "Employee", label: "员工" },
    { value: "Candidate", label: "候选人" },
    { value: "Department", label: "部门" },
    { value: "Position", label: "职位" },
];

/**
 * Schema列表组件
 */
export function SchemaList({
    onSelectSchema,
    onCreateSchema,
    onEditSchema,
    onCloneSchema,
}: SchemaListProps) {
    const [entityType, setEntityType] = useState<string>("all");
    const [pageParams] = useState<PageParams>({
        page: 1,
        limit: 100, // 一次加载较多数据，避免分页
    });
    const { toast } = useToast();

    // 获取Schema列表，所有实体类型
    const { data, error, isLoading, mutate } = useSchemaList(
        entityType === "all" ? "General" : entityType,
        pageParams,
        undefined, // 所有公司
        true // 包含系统Schema
    );

    // 处理删除Schema
    const handleDeleteSchema = async (schema: JsonSchemaSchema) => {
        if (!confirm(`确定要删除模板 "${schema.name}" 吗？此操作不可恢复。`)) {
            return;
        }

        try {
            await deleteJsonSchema(schema.id);
            toast({
                title: "成功",
                description: "删除模板成功",
            });
            mutate(); // 刷新数据
        } catch (error) {
            console.error("删除模板失败:", error);
            toast({
                title: "错误",
                description: "删除模板失败，可能有数据正在使用此模板",
                variant: "destructive",
            });
        }
    };

    // 处理创建Schema
    const handleCreateSchema = () => {
        const type = entityType === "all" ? "Company" : entityType;
        onCreateSchema?.(type);
    };

    // 根据实体类型筛选Schema列表
    const filteredSchemas = data?.data.filter((schema) => {
        if (entityType === "all") return true;
        return schema.entity_type === entityType;
    }) || [];

    if (isLoading) {
        return (
            <div className="flex justify-center p-8">
                <LoadingSpinner className="mr-2" />
                加载中...
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center text-destructive">
                加载失败: {error.message}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <div className="flex items-center space-x-4">
                    <h2 className="text-lg font-medium">自定义字段模板</h2>
                    <Select value={entityType} onValueChange={setEntityType}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="选择实体类型" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectGroup>
                                <SelectLabel>实体类型</SelectLabel>
                                {ENTITY_TYPE_OPTIONS.map((option) => (
                                    <SelectItem key={option.value} value={option.value}>
                                        {option.label}
                                    </SelectItem>
                                ))}
                            </SelectGroup>
                        </SelectContent>
                    </Select>
                </div>
                <Button onClick={handleCreateSchema}>
                    <Plus className="h-4 w-4 mr-1" />
                    新建模板
                </Button>
            </div>

            {filteredSchemas.length === 0 ? (
                <Card className="flex flex-col items-center justify-center p-8 text-center">
                    <p className="text-muted-foreground mb-4">暂无自定义字段模板</p>
                    <Button onClick={handleCreateSchema} variant="outline">
                        <Plus className="h-4 w-4 mr-1" />
                        创建模板
                    </Button>
                </Card>
            ) : (
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>ID</TableHead>
                            <TableHead>名称</TableHead>
                            <TableHead>实体类型</TableHead>
                            <TableHead>所属</TableHead>
                            <TableHead>版本</TableHead>
                            <TableHead>操作</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {filteredSchemas.map((schema) => (
                            <TableRow key={schema.id}>
                                <TableCell>{schema.id}</TableCell>
                                <TableCell>
                                    <div className="font-medium">{schema.name}</div>
                                    <div className="text-xs text-muted-foreground">
                                        {schema.remark || "无描述"}
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <Badge variant="outline">
                                        {
                                            ENTITY_TYPE_OPTIONS.find(
                                                (option) => option.value === schema.entity_type
                                            )?.label || schema.entity_type
                                        }
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    {schema.is_system ? (
                                        <Badge variant="secondary">系统</Badge>
                                    ) : schema.company_id ? (
                                        <Badge>公司ID: {schema.company_id}</Badge>
                                    ) : (
                                        <Badge variant="outline">通用</Badge>
                                    )}
                                </TableCell>
                                <TableCell>v{schema.version}</TableCell>
                                <TableCell>
                                    <div className="flex items-center space-x-2">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => onEditSchema?.(schema)}
                                            disabled={schema.is_system}
                                        >
                                            <PencilIcon className="h-4 w-4 mr-1" />
                                            编辑
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => onCloneSchema?.(schema)}
                                        >
                                            <Copy className="h-4 w-4 mr-1" />
                                            克隆
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleDeleteSchema(schema)}
                                            disabled={schema.is_system}
                                        >
                                            <Trash2 className="h-4 w-4 mr-1" />
                                            删除
                                        </Button>
                                    </div>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            )}
        </div>
    );
}