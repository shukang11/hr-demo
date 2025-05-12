/**
 * Schema编辑器组件
 * 
 * 用于创建和修改自定义字段模板，包括Schema结构和UI配置。
 * 支持公司拥有者创建和管理专属于其公司的自定义字段。
 */
import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
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
import { Alert, AlertDescription } from "@/components/ui/alert";
import { InfoIcon, Wand2 } from "lucide-react";
import { SchemaPreview } from "./schema-preview"; // 导入预览组件

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
     * 当前用户的公司ID，用于创建绑定到公司的Schema
     */
    defaultCompanyId?: number;

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

// 热门字段类型模板
const FIELD_TEMPLATES = {
    text: {
        type: "string",
        title: "文本字段",
    },
    number: {
        type: "number",
        title: "数字字段",
    },
    date: {
        type: "string",
        format: "date",
        title: "日期字段",
    },
    email: {
        type: "string",
        format: "email",
        title: "电子邮箱",
    },
    tel: {
        type: "string",
        format: "tel",
        pattern: "^\\d{3}-\\d{3,4}-\\d{4}$",
        title: "电话号码",
    },
    select: {
        type: "string",
        enum: ["选项1", "选项2", "选项3"],
        title: "下拉选择",
    },
    multiSelect: {
        type: "array",
        items: {
            type: "string",
            enum: ["选项1", "选项2", "选项3"],
        },
        uniqueItems: true,
        title: "多选字段",
    },
    boolean: {
        type: "boolean",
        title: "是/否字段",
    },
};

/**
 * Schema编辑器组件
 */
export function SchemaEditor({
    open,
    onOpenChange,
    schema,
    defaultEntityType = "Company",
    defaultCompanyId,
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
    const [showTemplates, setShowTemplates] = useState<boolean>(false);
    const [isPreviewOpen, setIsPreviewOpen] = useState<boolean>(true); // 是否显示预览

    const { toast } = useToast();
    const isEditing = !!schema;

    // 初始化表单数据
    useEffect(() => {
        if (schema) {
            setName(schema.name);
            setEntityType(schema.entity_type);
            setRemark(schema.remark || "");
            setSchemaJson(JSON.stringify(schema.schema_value, null, 2));
            setUiSchemaJson(JSON.stringify(schema.ui_schema || {}, null, 2));
        } else {
            setName("");
            setEntityType(defaultEntityType);
            setRemark("");
            setSchemaJson(JSON.stringify(DEFAULT_SCHEMA, null, 2));
            setUiSchemaJson(JSON.stringify(DEFAULT_UI_SCHEMA, null, 2));
        }
        setError(null);
        setShowTemplates(false);
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

    // 插入字段模板
    const insertFieldTemplate = (templateKey: keyof typeof FIELD_TEMPLATES) => {
        try {
            const currentSchema = JSON.parse(schemaJson);
            if (!currentSchema.properties) {
                currentSchema.properties = {};
            }

            // 生成一个唯一的字段名
            let fieldName = `field_${Date.now().toString().slice(-6)}`;
            currentSchema.properties[fieldName] = FIELD_TEMPLATES[templateKey];

            setSchemaJson(JSON.stringify(currentSchema, null, 2));
            setShowTemplates(false);
        } catch (e) {
            setError("无法添加字段，Schema格式可能不正确");
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
                    schema_value: JSON.parse(schemaJson), // 修改处
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
                    schema_value: JSON.parse(schemaJson), // 修改处
                    ui_schema: uiSchemaJson ? JSON.parse(uiSchemaJson) : undefined,
                    remark: remark || undefined,
                    is_system: false,
                    // 公司拥有者模式：为自定义字段指定公司ID
                    company_id: defaultCompanyId,
                };

                console.log("Frontend: createData to be sent:", JSON.stringify(createData, null, 2));

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

    // 使用AI生成字段
    const handleGenerateWithAI = async () => {
        // 示例函数，实际中可能需要调用后端API或OpenAI等服务
        toast({
            title: "功能开发中",
            description: "AI字段生成功能正在开发中，敬请期待"
        });
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-[95vw] md:max-w-5xl h-[90vh]">
                <DialogHeader>
                    <DialogTitle>
                        {isEditing ? "编辑自定义字段模板" : "新建自定义字段模板"}
                    </DialogTitle>
                    {defaultCompanyId && (
                        <DialogDescription>
                            创建的自定义字段将绑定到您的公司，仅对您的公司可见。
                        </DialogDescription>
                    )}
                </DialogHeader>

                <div className="flex flex-col md:flex-row gap-4">
                    {/* 左侧：编辑区域 */}
                    <div className="flex-1 min-w-0 max-h-[calc(90vh-12rem)] overflow-auto">
                        <div className="grid gap-4">
                            {/* 错误提示 */}
                            {error && (
                                <div className="bg-destructive/10 text-destructive p-3 rounded-md text-sm">
                                    {error}
                                </div>
                            )}

                            {/* 基本信息 */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

                                <TabsContent value="schema" className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <Label className="text-sm flex items-center">
                                            Schema定义
                                            <a
                                                href="https://json-schema.org/understanding-json-schema/"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-primary ml-2"
                                            >
                                                查看文档
                                            </a>
                                        </Label>
                                        <div className="flex space-x-2">
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="sm"
                                                onClick={handleGenerateWithAI}
                                            >
                                                <Wand2 className="h-4 w-4 mr-1" />
                                                AI生成字段
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="outline"
                                                size="sm"
                                                onClick={() => setShowTemplates(!showTemplates)}
                                            >
                                                添加常用字段
                                            </Button>
                                        </div>
                                    </div>

                                    {/* 字段模板选择器 */}
                                    {showTemplates && (
                                        <div className="bg-muted p-3 rounded-md text-sm mb-2">
                                            <h4 className="font-medium mb-2">选择要添加的字段类型:</h4>
                                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                                                {Object.keys(FIELD_TEMPLATES).map((key) => (
                                                    <Button
                                                        key={key}
                                                        variant="secondary"
                                                        size="sm"
                                                        className="justify-start"
                                                        onClick={() => insertFieldTemplate(key as keyof typeof FIELD_TEMPLATES)}
                                                    >
                                                        {FIELD_TEMPLATES[key as keyof typeof FIELD_TEMPLATES].title}
                                                    </Button>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <Textarea
                                        value={schemaJson}
                                        onChange={(e) => setSchemaJson(e.target.value)}
                                        className="font-mono h-[250px] text-sm"
                                    />
                                </TabsContent>

                                <TabsContent value="ui" className="space-y-2">
                                    <div className="flex justify-between items-start">
                                        <Label className="text-sm">
                                            UI配置
                                            <a
                                                href="https://react-jsonschema-form.readthedocs.io/en/latest/api-reference/uiSchema/"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-primary ml-2"
                                            >
                                                查看文档
                                            </a>
                                        </Label>
                                    </div>

                                    <Alert className="mb-2">
                                        <InfoIcon className="h-4 w-4" />
                                        <AlertDescription>
                                            UI配置是可选的，用于自定义表单的外观和行为。如果不确定，可以留空系统会使用默认样式。
                                        </AlertDescription>
                                    </Alert>

                                    <Textarea
                                        value={uiSchemaJson}
                                        onChange={(e) => setUiSchemaJson(e.target.value)}
                                        className="font-mono h-[250px] text-sm"
                                    />
                                </TabsContent>
                            </Tabs>
                        </div>
                    </div>

                    {/* 右侧：预览区域 */}
                    <div className="flex flex-col flex-1 min-w-0">
                        <div className="mb-2 flex justify-between items-center">
                            <h3 className="text-sm font-medium">实时预览</h3>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setIsPreviewOpen(!isPreviewOpen)}
                            >
                                {isPreviewOpen ? "隐藏预览" : "显示预览"}
                            </Button>
                        </div>

                        {isPreviewOpen && (
                            <div className="flex-1 overflow-auto">
                                <SchemaPreview
                                    schema={schemaJson}
                                    uiSchema={uiSchemaJson}
                                    entityType={
                                        ENTITY_TYPE_OPTIONS.find(opt => opt.value === entityType)?.label || entityType
                                    }
                                    title={name || "自定义字段预览"}
                                />
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex justify-end gap-2 pt-4 border-t mt-4">
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