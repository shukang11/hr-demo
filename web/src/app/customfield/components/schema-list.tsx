/**
 * Schema列表组件
 * 
 * 展示所有可用的自定义字段模板，支持按实体类型筛选。
 * 针对公司拥有者角色进行了优化，自动筛选其所属公司的自定义字段。
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
import { AlertCircle, Copy, InfoIcon, PencilIcon, Plus, RefreshCcw, Search, Trash2 } from "lucide-react";
import {
    JsonSchemaSchema,
    deleteJsonSchema,
    useSchemaList,
} from "@/lib/api/customfield";
import { PageParams } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

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

    /**
     * 当前用户的公司ID（公司拥有者）
     */
    currentCompanyId?: number;

    /**
     * 是否为系统管理员
     */
    isAdmin?: boolean;
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
    currentCompanyId,
    isAdmin = false,
}: SchemaListProps) {
    // 活跃的标签页
    const [activeTab, setActiveTab] = useState<string>("company");

    // 基础状态
    const [entityType, setEntityType] = useState<string>("all");
    const [searchTerm, setSearchTerm] = useState<string>("");
    const [pageParams] = useState<PageParams>({
        page: 1,
        limit: 100, // 一次加载较多数据，避免分页
    });
    const { toast } = useToast();

    // 获取Schema列表
    const { data, error, isLoading, mutate } = useSchemaList(
        entityType,
        pageParams,
        // 公司拥有者模式：强制使用当前公司ID
        currentCompanyId,
        true // 总是包含系统预设
    );

    // 检查特定的错误类型
    const isPermissionError = error?.message?.includes('Permission') ||
        error?.message?.includes('permission') ||
        error?.message?.toLowerCase()?.includes('权限') ||
        error?.message?.includes('is_super_admin');

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

    // 刷新数据
    const handleRefresh = () => {
        mutate();
    };

    // 判断Schema是否可编辑
    const canEditSchema = (schema: JsonSchemaSchema) => {
        // 系统管理员可以编辑任何非系统模板
        if (isAdmin) return !schema.is_system;

        // 公司拥有者只能编辑自己公司的模板
        return schema.company_id === currentCompanyId && !schema.is_system;
    };

    // 判断Schema是否可删除
    const canDeleteSchema = (schema: JsonSchemaSchema) => {
        // 与可编辑条件相同
        return canEditSchema(schema);
    };

    // 筛选数据
    const filteredSchemas = data?.items.filter(schema => {
        // 搜索词过滤
        if (searchTerm) {
            const searchLower = searchTerm.toLowerCase();
            const nameMatch = schema.name.toLowerCase().includes(searchLower);
            const remarkMatch = schema.remark?.toLowerCase()?.includes(searchLower);
            if (!nameMatch && !remarkMatch) return false;
        }

        // 标签页筛选
        if (activeTab === "company") {
            // 公司页签：显示当前公司的自定义模板
            return schema.company_id === currentCompanyId;
        } else if (activeTab === "system") {
            // 系统页签：显示系统预设的模板
            return schema.is_system;
        } else if (activeTab === "common") {
            // 通用页签：显示通用模板（无公司ID）
            return !schema.is_system && !schema.company_id;
        }

        return true;
    }) || [];

    // 计算各分类数量
    const companyCount = data?.items.filter(s => s.company_id === currentCompanyId).length || 0;
    const systemCount = data?.items.filter(s => s.is_system).length || 0;
    const commonCount = data?.items.filter(s => !s.is_system && !s.company_id).length || 0;

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
            <Alert variant="destructive" className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>无法加载自定义字段</AlertTitle>
                <AlertDescription className="space-y-2">
                    <p>
                        {isPermissionError
                            ? "您没有权限查看自定义字段。这可能是因为系统权限模块出现了问题或您的账户需要重新授权。"
                            : `加载失败: ${error.message}`
                        }
                    </p>
                    <div className="flex justify-end">
                        <Button variant="outline" size="sm" onClick={() => mutate()}>
                            <RefreshCcw className="h-4 w-4 mr-1" />
                            重试
                        </Button>
                    </div>
                </AlertDescription>
            </Alert>
        );
    }

    return (
        <div className="space-y-4">
            {/* 标题和操作区域 */}
            <div className="flex flex-col space-y-4">
                <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-4">
                        <h2 className="text-lg font-medium">自定义字段管理</h2>
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button variant="ghost" size="icon">
                                        <InfoIcon className="w-4 h-4" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p className="max-w-xs">
                                        自定义字段允许您为不同类型的实体（如员工、候选人、部门等）添加额外的信息字段。
                                        公司拥有者可以创建和管理适用于自己公司的自定义字段模板。
                                    </p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                        <Button variant="outline" size="sm" onClick={handleRefresh}>
                            <RefreshCcw className="h-4 w-4 mr-1" />
                            刷新
                        </Button>
                    </div>

                    <Button onClick={handleCreateSchema}>
                        <Plus className="h-4 w-4 mr-1" />
                        新建自定义字段
                    </Button>
                </div>

                {/* 搜索和分类过滤 */}
                <div className="flex justify-between items-center">
                    <div className="flex-1 max-w-sm relative">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="搜索自定义字段..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-8"
                        />
                    </div>

                    <div className="flex items-center space-x-4">
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
                </div>
            </div>

            {/* 使用Tabs分类展示 */}
            <Tabs defaultValue="company" value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    {/* 只有在当前用户有公司时才显示"我的公司"标签 */}
                    {currentCompanyId && (
                        <TabsTrigger value="company">
                            我的公司 <Badge variant="secondary" className="ml-1">{companyCount}</Badge>
                        </TabsTrigger>
                    )}
                    <TabsTrigger value="system">
                        系统预设 <Badge variant="secondary" className="ml-1">{systemCount}</Badge>
                    </TabsTrigger>
                    <TabsTrigger value="common">
                        通用模板 <Badge variant="secondary" className="ml-1">{commonCount}</Badge>
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="company" className="mt-4">
                    {!currentCompanyId ? (
                        <Alert className="mb-4">
                            <AlertTitle>未关联公司</AlertTitle>
                            <AlertDescription>
                                您的账号未关联到任何公司，无法管理公司自定义字段。请联系系统管理员关联公司。
                            </AlertDescription>
                        </Alert>
                    ) : (
                        renderSchemaTable(filteredSchemas)
                    )}
                </TabsContent>

                <TabsContent value="system" className="mt-4">
                    {activeTab === "system" && (
                        <Alert className="mb-4">
                            <AlertTitle>系统预设字段</AlertTitle>
                            <AlertDescription>
                                系统预设字段是由系统管理员提供的标准字段模板。您可以查看和克隆这些模板，但不能直接修改它们。
                            </AlertDescription>
                        </Alert>
                    )}
                    {renderSchemaTable(filteredSchemas)}
                </TabsContent>

                <TabsContent value="common" className="mt-4">
                    {activeTab === "common" && (
                        <Alert className="mb-4">
                            <AlertTitle>通用字段模板</AlertTitle>
                            <AlertDescription>
                                通用字段模板适用于所有公司。您可以克隆这些模板到自己的公司并进行自定义修改。
                            </AlertDescription>
                        </Alert>
                    )}
                    {renderSchemaTable(filteredSchemas)}
                </TabsContent>
            </Tabs>
        </div>
    );

    // 渲染Schema表格
    function renderSchemaTable(schemas: JsonSchemaSchema[]) {
        if (schemas.length === 0) {
            return (
                <Card className="flex flex-col items-center justify-center p-8 text-center">
                    <p className="text-muted-foreground mb-4">
                        {activeTab === "company"
                            ? "您的公司暂无自定义字段模板"
                            : activeTab === "system"
                                ? "暂无系统预设字段模板"
                                : "暂无通用字段模板"}
                    </p>
                    {activeTab === "company" && (
                        <div className="space-y-2 w-full max-w-md">
                            <Button onClick={handleCreateSchema} className="w-full">
                                <Plus className="h-4 w-4 mr-1" />
                                创建自定义字段
                            </Button>
                            <p className="text-xs text-muted-foreground">或从系统预设和通用模板中克隆</p>
                        </div>
                    )}
                </Card>
            );
        }

        return (
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>名称</TableHead>
                        <TableHead>实体类型</TableHead>
                        <TableHead>版本</TableHead>
                        <TableHead className="hidden md:table-cell">更新时间</TableHead>
                        <TableHead>操作</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {schemas.map((schema) => (
                        <TableRow key={schema.id}>
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
                            <TableCell>v{schema.version}</TableCell>
                            <TableCell className="hidden md:table-cell">
                                {schema.updated_at
                                    ? new Date(schema.updated_at).toLocaleDateString()
                                    : "未知"}
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center space-x-2">
                                    <TooltipProvider>
                                        <Tooltip>
                                            <TooltipTrigger asChild>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => onEditSchema?.(schema)}
                                                    disabled={!canEditSchema(schema)}
                                                >
                                                    <PencilIcon className="h-4 w-4 mr-1" />
                                                    编辑
                                                </Button>
                                            </TooltipTrigger>
                                            {!canEditSchema(schema) && (
                                                <TooltipContent>
                                                    {schema.is_system
                                                        ? "系统模板不可编辑，但可以克隆"
                                                        : "您没有权限编辑此模板"}
                                                </TooltipContent>
                                            )}
                                        </Tooltip>
                                    </TooltipProvider>

                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => onCloneSchema?.(schema)}
                                    >
                                        <Copy className="h-4 w-4 mr-1" />
                                        克隆
                                    </Button>

                                    {activeTab === "company" && (
                                        <TooltipProvider>
                                            <Tooltip>
                                                <TooltipTrigger asChild>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => handleDeleteSchema(schema)}
                                                        disabled={!canDeleteSchema(schema)}
                                                    >
                                                        <Trash2 className="h-4 w-4 mr-1" />
                                                        删除
                                                    </Button>
                                                </TooltipTrigger>
                                                {!canDeleteSchema(schema) && (
                                                    <TooltipContent>
                                                        {schema.is_system
                                                            ? "系统模板不可删除"
                                                            : "您没有权限删除此模板"}
                                                    </TooltipContent>
                                                )}
                                            </Tooltip>
                                        </TooltipProvider>
                                    )}
                                </div>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        );
    }
}