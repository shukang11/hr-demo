/**
 * Schema编辑器组件
 * 
 * 用于创建和修改自定义字段模板，包括Schema结构和UI配置。
 */
import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    JsonSchemaCreate,
    JsonSchemaSchema,
    JsonSchemaUpdate,
    createJsonSchema,
    updateJsonSchema,
} from "@/lib/api/customfield";

interface SchemaEditorProps {
    /**
     * 对话框是否打开
     */
    open: boolean;

    /**
     * 对话框打开状态变化回调
     */
    onOpenChange: (open: boolean) => void;

    /**
     * 要编辑的Schema，如果是新建则为null
     */
    schema?: JsonSchemaSchema | null;

    /**
     * 默认实体类型，用于新建时
     */
    defaultEntityType?: string;

    /**
     * 操作成功回调
     */
    onSuccess?: () => void;
}

const ENTITY_TYPE_OPTIONS = [
    { value: "Company", label: "公司" },
    { value: "Employee", label: "员工" },
    { value: "Candidate", label: "候选人" },
    { value: "Department", label: "部门" },
    { value: "Position", label: "职位" },
];

// 默认的JSON Schema结构
const DEFAULT_SCHEMA = {
    type: "object",
    properties: {
        sample: {
            type: "string",
            title: "示例字段"
        }
    }
};

// 默认的UI Schema结构
const DEFAULT_UI_SCHEMA = {
    sample: {
        "ui:placeholder": "请输入示例内容"
    }
};

/**
 * Schema编辑器组件
 */
export function SchemaEditor({
    open,
    onOpenChange,
    schema,
    defaultEntityType = "Company",
    onSuccess,
}: SchemaEditorProps) {
    // 表单状态
    const [name, setName] = useState<string>("");
    const [entityType, setEntityType] = useState<string>(defaultEntityType);
    const [remark, setRemark] = useState<string>("");
    const [schemaJson, setSchemaJson] = useState<string>("");
    const [uiSchemaJson, setUiSchemaJson] = useState<string>("");
    const [activeTab, setActiveTab] = useState<string>("schema");
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const { toast } = useToast();
    const isEditing = !!schema;

    // 初始化表单数据
    useEffect(() => {
        if (schema) {
            setName(schema.name);
            setEntityType(schema.entity_type);
            setRemark(schema.remark || "");
            setSchemaJson(JSON.stringify(schema.schema, null, 2));
            setUiSchemaJson(JSON.stringify(schema.ui_schema || {}, null, 2));
        } else {
            setName("");
            setEntityType(defaultEntityType);
            setRemark("");
            setSchemaJson(JSON.stringify(DEFAULT_SCHEMA, null, 2));
            setUiSchemaJson(JSON.stringify(DEFAULT_UI_SCHEMA, null, 2));
        }
        setError(null);
    }, [schema, defaultEntityType, open]);

    // 验证JSON格式
    const validateJson = (json: string): boolean => {
        try {
            JSON.parse(json);
            return true;
        } catch (e) {
            return false;
        }
    };

    // 处理表单提交
    const handleSubmit = async () => {
        // 基本验证
        if (!name.trim()) {
            setError("请输入模板名称");
            return;
        }

        // 验证JSON格式
        if (!validateJson(schemaJson)) {
            setError("Schema格式不正确，请检查JSON语法");
            setActiveTab("schema");
            return;
        }

        if (uiSchemaJson && !validateJson(uiSchemaJson)) {
            setError("UI Schema格式不正确，请检查JSON语法");
            setActiveTab("ui");
            return;
        }

        try {
            setLoading(true);
            setError(null);

            if (isEditing) {
                // 更新Schema
                const updateData: JsonSchemaUpdate = {
                    name,
                    schema: JSON.parse(schemaJson),
                    ui_schema: uiSchemaJson ? JSON.parse(uiSchemaJson) : undefined,
                    remark: remark || undefined,
                };

                await updateJsonSchema(schema.id, updateData);
                toast({
                    title: "成功",
                    description: "更新自定义字段模板成功",
                });
            } else {
                // 创建Schema
                const createData: JsonSchemaCreate = {
                    name,
                    entity_type: entityType,
                    schema: JSON.parse(schemaJson),
                    ui_schema: uiSchemaJson ? JSON.parse(uiSchemaJson) : undefined,
                    remark: remark || undefined,
                    is_system: false,
                };

                await createJsonSchema(createData);
                toast({
                    title: "成功",
                    description: "创建自定义字段模板成功",
                });
            }

            // 关闭对话框并刷新数据
            onOpenChange(false);
            onSuccess?.();
        } catch (e) {
            console.error("保存自定义字段模板失败:", e);
            setError(`保存失败: ${e instanceof Error ? e.message : "未知错误"}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-3xl h-[90vh]">
                <DialogHeader>
                    <DialogTitle>
                        {isEditing ? "编辑自定义字段模板" : "新建自定义字段模板"}
                    </DialogTitle>
                </DialogHeader>

                <div className="grid gap-4 py-4 max-h-[calc(90vh-12rem)] overflow-auto">
                    {/* 错误提示 */}
                    {error && (
                        <div className="bg-destructive/10 text-destructive p-3 rounded-md text-sm">
                            {error}
                        </div>
                    )}

                    {/* 基本信息 */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">模板名称</Label>
                            <Input
                                id="name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="输入模板名称"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="entity-type">适用实体</Label>
                            <Select
                                value={entityType}
                                onValueChange={setEntityType}
                                disabled={isEditing} // 编辑时不允许修改实体类型
                            >
                                <SelectTrigger id="entity-type">
                                    <SelectValue placeholder="选择适用实体" />
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

                    <div className="space-y-2">
                        <Label htmlFor="remark">备注说明</Label>
                        <Textarea
                            id="remark"
                            value={remark}
                            onChange={(e) => setRemark(e.target.value)}
                            placeholder="输入备注说明（可选）"
                            className="h-20"
                        />
                    </div>

                    {/* Schema编辑器 */}
                    <Tabs
                        value={activeTab}
                        onValueChange={setActiveTab}
                        className="w-full"
                    >
                        <TabsList className="grid grid-cols-2">
                            <TabsTrigger value="schema">Schema结构</TabsTrigger>
                            <TabsTrigger value="ui">UI配置</TabsTrigger>
                        </TabsList>
                        <TabsContent value="schema" className="space-y-2">
                            <Label className="text-sm">
                                Schema定义 (
                                <a
                                    href="https://json-schema.org/understanding-json-schema/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-primary"
                                >
                                    查看JSON Schema文档
                                </a>
                                )
                            </Label>
                            <Textarea
                                value={schemaJson}
                                onChange={(e) => setSchemaJson(e.target.value)}
                                className="font-mono h-[300px] text-sm"
                            />
                        </TabsContent>
                        <TabsContent value="ui" className="space-y-2">
                            <Label className="text-sm">
                                UI配置 (
                                <a
                                    href="https://react-jsonschema-form.readthedocs.io/en/latest/api-reference/uiSchema/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-primary"
                                >
                                    查看UI Schema文档
                                </a>
                                )
                            </Label>
                            <Textarea
                                value={uiSchemaJson}
                                onChange={(e) => setUiSchemaJson(e.target.value)}
                                className="font-mono h-[300px] text-sm"
                            />
                        </TabsContent>
                    </Tabs>
                </div>

                <div className="flex justify-end gap-2">
                    <Button
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        disabled={loading}
                    >
                        取消
                    </Button>
                    <Button onClick={handleSubmit} disabled={loading}>
                        {loading && <LoadingSpinner className="mr-2 h-4 w-4" />}
                        保存
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}