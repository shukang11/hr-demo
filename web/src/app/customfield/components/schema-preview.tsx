/**
 * 自定义字段预览组件
 * 
 * 提供实时预览功能，展示自定义字段的实际效果。
 * 支持测试数据输入和格式验证，帮助用户设计合适的自定义字段。
 */
import { useState, useEffect } from "react";
import { DynamicForm } from "@/components/customfield/dynamic-form";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { InfoIcon, RefreshCcw, Clipboard } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

interface SchemaPreviewProps {
    /**
     * JSON Schema定义
     */
    schema: Record<string, any> | string;

    /**
     * UI Schema配置，可选
     */
    uiSchema?: Record<string, any> | string;

    /**
     * 字段实体类型
     */
    entityType?: string;

    /**
     * 预览窗口标题
     */
    title?: string;

    /**
     * 自定义CSS类名
     */
    className?: string;
}

/**
 * 生成随机示例数据
 * 
 * 根据Schema类型生成相应的示例数据
 */
function generateSampleData(schema: Record<string, any>): Record<string, any> {
    const result: Record<string, any> = {};

    if (schema.type !== 'object' || !schema.properties) {
        return result;
    }

    // 遍历属性，为每个属性生成示例数据
    Object.entries(schema.properties).forEach(([key, propSchema]: [string, any]) => {
        switch (propSchema.type) {
            case 'string':
                if (propSchema.format === 'email') {
                    result[key] = 'example@company.com';
                } else if (propSchema.format === 'date') {
                    result[key] = new Date().toISOString().slice(0, 10);
                } else if (propSchema.format === 'tel') {
                    result[key] = '138-1234-5678';
                } else if (propSchema.enum && propSchema.enum.length > 0) {
                    result[key] = propSchema.enum[0];
                } else {
                    result[key] = propSchema.title || `${key}示例值`;
                }
                break;
            case 'number':
            case 'integer':
                result[key] = 42;
                break;
            case 'boolean':
                result[key] = true;
                break;
            case 'array':
                if (propSchema.items?.enum && propSchema.items.enum.length > 0) {
                    result[key] = [propSchema.items.enum[0]];
                } else {
                    result[key] = [];
                }
                break;
            case 'object':
                result[key] = generateSampleData(propSchema);
                break;
            default:
                result[key] = null;
        }
    });

    return result;
}

/**
 * Schema预览组件
 */
export function SchemaPreview({
    schema,
    uiSchema,
    entityType,
    title = "自定义字段预览",
    className,
}: SchemaPreviewProps) {
    // 解析Schema对象
    const [parsedSchema, setParsedSchema] = useState<Record<string, any>>({});
    const [parsedUiSchema, setParsedUiSchema] = useState<Record<string, any>>({});
    const [formData, setFormData] = useState<Record<string, any>>({});
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<string>("preview");

    // 处理Schema和UiSchema的变更
    useEffect(() => {
        try {
            // 解析Schema
            const schemaObj = typeof schema === 'string' ? JSON.parse(schema) : schema;
            setParsedSchema(schemaObj);

            // 解析UiSchema (可选)
            if (uiSchema) {
                const uiSchemaObj = typeof uiSchema === 'string' ? JSON.parse(uiSchema) : uiSchema;
                setParsedUiSchema(uiSchemaObj);
            } else {
                setParsedUiSchema({});
            }

            setError(null);
        } catch (e) {
            console.error("Schema解析错误:", e);
            setError("Schema格式不正确，无法预览");
        }
    }, [schema, uiSchema]);

    // 当Schema变更时生成示例数据
    useEffect(() => {
        if (Object.keys(parsedSchema).length > 0) {
            try {
                const sampleData = generateSampleData(parsedSchema);
                setFormData(sampleData);
            } catch (e) {
                console.error("生成示例数据错误:", e);
            }
        }
    }, [parsedSchema]);

    // 生成新的随机数据
    const handleGenerateSampleData = () => {
        if (Object.keys(parsedSchema).length > 0) {
            const sampleData = generateSampleData(parsedSchema);
            setFormData(sampleData);
        }
    };

    // 复制JSON数据到剪贴板
    const handleCopyJsonData = () => {
        try {
            navigator.clipboard.writeText(JSON.stringify(formData, null, 2));
        } catch (e) {
            console.error("复制到剪贴板失败:", e);
        }
    };

    // 表单数据变更处理
    const handleFormChange = (data: { formData: Record<string, any> }) => {
        setFormData(data.formData);
    };

    // 处理表单错误
    const handleFormError = (errors: any[]) => {
        if (errors && errors.length > 0) {
            console.log("表单验证错误:", errors);
        }
    };

    return (
        <Card className={cn("w-full", className)}>
            <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                    <CardTitle className="text-lg">{title}</CardTitle>
                    {entityType && (
                        <Badge variant="outline">{entityType}</Badge>
                    )}
                </div>
                <CardDescription>实时预览自定义字段的表单效果</CardDescription>
            </CardHeader>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="px-6">
                <TabsList>
                    <TabsTrigger value="preview">表单预览</TabsTrigger>
                    <TabsTrigger value="data">数据示例</TabsTrigger>
                </TabsList>

                <TabsContent value="preview" className="py-2">
                    {error ? (
                        <Alert variant="destructive" className="mb-2">
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    ) : (
                        <CardContent className="pt-0">
                            <DynamicForm
                                schema={parsedSchema}
                                uiSchema={parsedUiSchema}
                                formData={formData}
                                onChange={handleFormChange}
                                onError={handleFormError}
                                showSubmitButton={false}
                                className="mt-2"
                            />
                        </CardContent>
                    )}
                </TabsContent>

                <TabsContent value="data" className="py-2">
                    <CardContent className="pt-0">
                        <div className="mb-2 flex items-center text-sm text-muted-foreground">
                            <InfoIcon className="h-4 w-4 mr-1" />
                            这是当前表单数据的JSON结构，可用于测试或API调用
                        </div>
                        <pre className="bg-muted p-4 rounded-md overflow-auto text-xs max-h-[300px]">
                            {JSON.stringify(formData, null, 2)}
                        </pre>
                    </CardContent>
                </TabsContent>
            </Tabs>

            <CardFooter className="flex justify-between border-t pt-4 pb-2">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleGenerateSampleData}
                >
                    <RefreshCcw className="h-4 w-4 mr-1" />
                    生成示例数据
                </Button>

                <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleCopyJsonData}
                >
                    <Clipboard className="h-4 w-4 mr-1" />
                    复制JSON数据
                </Button>
            </CardFooter>
        </Card>
    );
}