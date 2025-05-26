/**
 * JSON Schema表单组件
 * 
 * 该组件可以根据传入的JSON Schema动态渲染表单字段
 * 支持基本的字段类型（字符串、数字、布尔值、枚举等）
 * 
 * @module components/ui/json-schema-form
 */
import { useEffect, useState } from "react";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
    FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "./card";

// 字段类型定义
type FieldType = "string" | "number" | "integer" | "boolean" | "array" | "object";

// UI展示配置接口
interface UiSchema {
    [key: string]: {
        "ui:widget"?: string;
        "ui:placeholder"?: string;
        "ui:description"?: string;
        "ui:className"?: string;
        [key: string]: any;
    };
}

// 字段属性接口
interface SchemaProperty {
    type: FieldType;
    title?: string;
    description?: string;
    default?: any;
    enum?: any[];
    enumNames?: string[];
    format?: string;
    minimum?: number;
    maximum?: number;
    minLength?: number;
    maxLength?: number;
    pattern?: string;
    required?: boolean;
    properties?: Record<string, SchemaProperty>;
    items?: SchemaProperty;
}

// Schema接口
interface Schema {
    type: FieldType;
    title?: string;
    description?: string;
    properties: Record<string, SchemaProperty>;
    required?: string[];
}

interface JsonSchemaFormProps {
    /**
     * JSON Schema定义
     */
    schema: Schema;
    /**
     * UI展示相关的配置
     */
    uiSchema?: UiSchema;
    /**
     * 初始值
     */
    initialValue?: Record<string, any>;
    /**
     * 值变化时的回调函数
     */
    onChange?: (value: Record<string, any>) => void;
    /**
     * 提交表单时的回调函数
     */
    onSubmit?: (value: Record<string, any>) => void;
    /**
     * 禁用整个表单
     */
    disabled?: boolean;
    /**
     * 自定义类名
     */
    className?: string;
    /**
     * 是否显示为卡片形式
     */
    asCard?: boolean;
    /**
     * 卡片标题（仅在asCard=true时有效）
     */
    cardTitle?: string;
}

/**
 * 根据JSON Schema构建Zod验证Schema
 * 
 * @param schema JSON Schema定义
 * @returns Zod Schema对象
 */
function buildZodSchema(schema: Schema): z.ZodType {
    // 构建用于每个属性的Zod验证规则
    const schemaObj: Record<string, any> = {};
    const required = schema.required || [];

    for (const [key, property] of Object.entries(schema.properties)) {
        let fieldSchema: z.ZodType;

        // 根据字段类型创建对应的Zod验证规则
        switch (property.type) {
            case "string":
                let stringSchema = z.string();
                if (property.minLength) {
                    stringSchema = stringSchema.min(property.minLength, {
                        message: `必须至少包含${property.minLength}个字符`,
                    });
                }
                if (property.maxLength) {
                    stringSchema = stringSchema.max(property.maxLength, {
                        message: `不能超过${property.maxLength}个字符`,
                    });
                }
                fieldSchema = stringSchema;
                if (property.pattern) {
                    fieldSchema = (fieldSchema as z.ZodString).regex(new RegExp(property.pattern), {
                        message: property.description || "格式不正确",
                    });
                }
                if (property.enum) {
                    fieldSchema = z.enum(property.enum as [string, ...string[]]);
                }
                if (property.format === "email") {
                    fieldSchema = z.string().email("请输入有效的邮箱地址");
                }
                break;
            case "number":
            case "integer":
                let numberSchema = property.type === "integer" ? z.number().int() : z.number();
                if (property.minimum !== undefined) {
                    numberSchema = numberSchema.min(property.minimum, {
                        message: `不能小于${property.minimum}`,
                    });
                }
                if (property.maximum !== undefined) {
                    numberSchema = numberSchema.max(property.maximum, {
                        message: `不能大于${property.maximum}`,
                    });
                }
                fieldSchema = numberSchema;
                break;
            case "boolean":
                fieldSchema = z.boolean();
                break;
            case "object":
                if (property.properties) {
                    fieldSchema = buildZodSchema({
                        type: "object",
                        properties: property.properties,
                        required: [],
                    });
                } else {
                    fieldSchema = z.record(z.any());
                }
                break;
            case "array":
                if (property.items) {
                    // Create a schema for the array items directly
                    let itemSchema: z.ZodType;

                    switch (property.items.type) {
                        case "string":
                            itemSchema = z.string();
                            break;
                        case "number":
                        case "integer":
                            itemSchema = property.items.type === "integer" ? z.number().int() : z.number();
                            break;
                        case "boolean":
                            itemSchema = z.boolean();
                            break;
                        case "object":
                            itemSchema = buildZodSchema({
                                type: "object",
                                properties: property.items.properties || {},
                                required: [],
                            });
                            break;
                        default:
                            itemSchema = z.any();
                    }

                    fieldSchema = z.array(itemSchema);
                } else {
                    fieldSchema = z.array(z.any());
                }
                break;
            default:
                fieldSchema = z.any();
        }

        // 处理必填字段
        if (required.includes(key)) {
            schemaObj[key] = fieldSchema;
        } else {
            schemaObj[key] = fieldSchema.optional().nullable();
        }
    }

    return z.object(schemaObj);
}

/**
 * 根据字段定义渲染表单控件
 * 
 * @param field 字段定义
 * @param name 字段名
 * @param control 表单控制器
 * @param uiSchema UI展示配置
 * @param disabled 是否禁用
 * @returns 表单控件
 */
const renderField = (
    field: SchemaProperty,
    name: string,
    control: any,
    uiSchema: UiSchema = {},
    disabled: boolean = false
) => {
    const ui = uiSchema[name] || {};
    const widget = ui["ui:widget"];

    // 根据字段类型和UI配置渲染不同的控件
    if (field.type === "string") {
        if (field.enum) {
            // 枚举类型，渲染下拉选择框
            return (
                <FormField
                    control={control}
                    name={name}
                    render={({ field: formField }) => (
                        <FormItem>
                            <FormLabel>{field.title || name}</FormLabel>
                            <Select
                                disabled={disabled}
                                onValueChange={formField.onChange}
                                defaultValue={formField.value}
                                value={formField.value || ""}
                            >
                                <FormControl>
                                    <SelectTrigger className={ui["ui:className"]}>
                                        <SelectValue placeholder={ui["ui:placeholder"] || `请选择${field.title || name}`} />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {field.enum?.map((value: string, index: number) => (
                                        <SelectItem key={value} value={value}>
                                            {field.enumNames?.[index] || value}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            {field.description && <FormDescription>{field.description}</FormDescription>}
                            <FormMessage />
                        </FormItem>
                    )}
                />
            );
        } else if (widget === "textarea") {
            // 多行文本
            return (
                <FormField
                    control={control}
                    name={name}
                    render={({ field: formField }) => (
                        <FormItem>
                            <FormLabel>{field.title || name}</FormLabel>
                            <FormControl>
                                <Textarea
                                    placeholder={ui["ui:placeholder"]}
                                    {...formField}
                                    value={formField.value || ""}
                                    disabled={disabled}
                                    className={ui["ui:className"]}
                                />
                            </FormControl>
                            {field.description && <FormDescription>{field.description}</FormDescription>}
                            <FormMessage />
                        </FormItem>
                    )}
                />
            );
        } else {
            // 默认单行文本输入框
            return (
                <FormField
                    control={control}
                    name={name}
                    render={({ field: formField }) => (
                        <FormItem>
                            <FormLabel>{field.title || name}</FormLabel>
                            <FormControl>
                                <Input
                                    type={widget === "password" ? "password" : widget === "email" ? "email" : "text"}
                                    placeholder={ui["ui:placeholder"]}
                                    {...formField}
                                    value={formField.value || ""}
                                    disabled={disabled}
                                    className={ui["ui:className"]}
                                />
                            </FormControl>
                            {field.description && <FormDescription>{field.description}</FormDescription>}
                            <FormMessage />
                        </FormItem>
                    )}
                />
            );
        }
    } else if (field.type === "number" || field.type === "integer") {
        // 数字输入框
        return (
            <FormField
                control={control}
                name={name}
                render={({ field: formField }) => (
                    <FormItem>
                        <FormLabel>{field.title || name}</FormLabel>
                        <FormControl>
                            <Input
                                type="number"
                                placeholder={ui["ui:placeholder"]}
                                {...formField}
                                onChange={(e) => {
                                    const value = e.target.value ? Number(e.target.value) : null;
                                    formField.onChange(value);
                                }}
                                value={formField.value ?? ""}
                                disabled={disabled}
                                min={field.minimum}
                                max={field.maximum}
                                className={ui["ui:className"]}
                            />
                        </FormControl>
                        {field.description && <FormDescription>{field.description}</FormDescription>}
                        <FormMessage />
                    </FormItem>
                )}
            />
        );
    } else if (field.type === "boolean") {
        // 布尔选择框
        return (
            <FormField
                control={control}
                name={name}
                render={({ field: formField }) => (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                        <FormControl>
                            <Checkbox
                                checked={formField.value}
                                onCheckedChange={formField.onChange}
                                disabled={disabled}
                            />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                            <FormLabel>{field.title || name}</FormLabel>
                            {field.description && <FormDescription>{field.description}</FormDescription>}
                        </div>
                        <FormMessage />
                    </FormItem>
                )}
            />
        );
    }

    // 不支持的字段类型
    return (
        <FormItem>
            <FormLabel>{field.title || name}</FormLabel>
            <FormDescription>不支持的字段类型: {field.type}</FormDescription>
            <FormMessage />
        </FormItem>
    );
};

/**
 * JSON Schema表单组件
 * 根据传入的JSON Schema定义动态渲染表单字段
 */
export function JsonSchemaForm({
    schema,
    uiSchema = {},
    initialValue = {},
    onChange,
    onSubmit,
    disabled = false,
    className,
    asCard = false,
    cardTitle,
}: JsonSchemaFormProps) {
    // 构建Zod验证Schema
    const [zodSchema, setZodSchema] = useState<z.ZodType | null>(null);

    useEffect(() => {
        try {
            const builtSchema = buildZodSchema(schema);
            setZodSchema(builtSchema);
        } catch (error) {
            console.error("创建Zod验证Schema失败:", error);
            setZodSchema(null);
        }
    }, [schema]);

    const form = useForm<Record<string, any>>({
        resolver: zodSchema ? zodResolver(zodSchema) : undefined,
        defaultValues: initialValue,
    });

    // 监听表单值变化并调用onChange回调
    useEffect(() => {
        const subscription = form.watch((value) => {
            onChange?.(value);
        });
        return () => subscription.unsubscribe();
    }, [form, onChange]);

    // 当initialValue变化时更新表单默认值
    useEffect(() => {
        if (initialValue && Object.keys(initialValue).length > 0) {
            form.reset(initialValue);
        }
    }, [initialValue, form]);

    // 提交表单处理函数
    const handleSubmit = form.handleSubmit((data) => {
        onSubmit?.(data);
    });

    // 如果Schema未构建完成，则不渲染表单
    if (!zodSchema) {
        return <div>加载表单定义中...</div>;
    }

    const formContent = (
        <Form {...form}>
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* 遍历Schema属性，渲染表单字段 */}
                {Object.entries(schema.properties).map(([name, field]) => (
                    <div key={name}>
                        {renderField(field, name, form.control, uiSchema, disabled)}
                    </div>
                ))}
            </form>
        </Form>
    );

    // 是否渲染为卡片形式
    if (asCard) {
        return (
            <Card className={cn("", className)}>
                {cardTitle && (
                    <CardHeader>
                        <CardTitle>{cardTitle}</CardTitle>
                    </CardHeader>
                )}
                <CardContent>{formContent}</CardContent>
            </Card>
        );
    }

    return <div className={cn("", className)}>{formContent}</div>;
}

export default JsonSchemaForm;
