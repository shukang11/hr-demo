/**
 * 自定义字段编辑器组件
 * 
 * 结合Schema选择和动态表单，提供完整的自定义字段编辑体验。
 */
import { JsonSchemaSchema, useSchema } from '@/lib/api/customfield';
import { SchemaSelector } from './schema-selector';
import { DynamicForm } from './dynamic-form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from '@/components/ui/skeleton';

export interface CustomFieldEditorProps {
    /**
     * 实体类型
     */
    entityType: string;

    /**
     * 实体ID，如果是新实体则不提供
     */
    entityId?: number;

    /**
     * 公司ID
     */
    companyId?: number;

    /**
     * 当前选中的Schema ID
     */
    schemaId?: number | null;

    /**
     * Schema变更回调函数
     */
    onSchemaChange?: (schemaId: number | null) => void;

    /**
     * 当前表单数据
     */
    formData?: Record<string, any>;

    /**
     * 表单数据变更回调函数
     */
    onFormDataChange?: (formData: Record<string, any>) => void;

    /**
     * 创建新Schema的回调函数
     */
    onCreateNewSchema?: () => void;

    /**
     * 是否禁用编辑器，默认为false
     */
    disabled?: boolean;

    /**
     * 是否只读模式，默认为false
     */
    readonly?: boolean;

    /**
     * 是否隐藏Schema选择器，默认为false
     * 当设置为true时，将只显示表单内容，不显示Schema选择器
     */
    hideSchemaSelector?: boolean;
}

/**
 * 自定义字段编辑器
 * 
 * 提供Schema选择和表单编辑的完整体验。
 * 
 * @example
 * ```tsx
 * <CustomFieldEditor 
 *   entityType="Company"
 *   companyId={company.id}
 *   schemaId={formData.extra_schema_id}
 *   onSchemaChange={(id) => setFormData({...formData, extra_schema_id: id})}
 *   formData={formData.extra_value}
 *   onFormDataChange={(data) => setFormData({...formData, extra_value: data})}
 * />
 * ```
 */
export function CustomFieldEditor({
    entityType,
    entityId,
    companyId,
    schemaId,
    onSchemaChange,
    formData,
    onFormDataChange,
    onCreateNewSchema,
    disabled = false,
    readonly = false,
    hideSchemaSelector = false,
}: CustomFieldEditorProps) {
    // 从API获取Schema详情
    const { data: schema, error, isLoading } = useSchema(schemaId ?? undefined);

    // 当表单数据变更时调用父组件的回调
    const handleFormChange = (data: { formData: Record<string, any> }) => {
        onFormDataChange?.(data.formData);
    };

    return (
        <div className="custom-field-editor space-y-4">
            {/* Schema选择器 */}
            {!readonly && !hideSchemaSelector && (
                <SchemaSelector
                    entityType={entityType}
                    value={schemaId ?? null}
                    onChange={onSchemaChange}
                    companyId={companyId}
                    onCreateNew={onCreateNewSchema}
                    disabled={disabled}
                />
            )}

            {/* 动态表单 */}
            {schemaId ? (
                isLoading ? (
                    <Card>
                        <CardHeader>
                            <Skeleton className="h-4 w-[250px]" />
                            <Skeleton className="h-4 w-[200px]" />
                        </CardHeader>
                        <CardContent>
                            <Skeleton className="h-[200px] w-full" />
                        </CardContent>
                    </Card>
                ) : error ? (
                    <Card className="border-destructive">
                        <CardHeader>
                            <CardTitle className="text-destructive">加载失败</CardTitle>
                            <CardDescription>无法加载自定义字段模板</CardDescription>
                        </CardHeader>
                        <CardContent>
                            请确认您选择的模板是否存在，或者尝试刷新页面。
                        </CardContent>
                    </Card>
                ) : schema ? (
                    <Card>
                        <CardHeader>
                            <CardTitle>{schema.name}</CardTitle>
                            {schema.remark && <CardDescription>{schema.remark}</CardDescription>}
                        </CardHeader>
                        <CardContent>
                            {schema.schema_value ? (
                                <DynamicForm
                                    schema={schema.schema_value as any}
                                    uiSchema={schema.ui_schema || undefined}
                                    formData={formData}
                                    onChange={handleFormChange}
                                    disabled={disabled}
                                    readonly={readonly}
                                    showSubmitButton={false}
                                />
                            ) : (
                                <div className="text-amber-500">
                                    自定义字段模板格式有误，请联系管理员检查模板配置
                                </div>
                            )}
                        </CardContent>
                    </Card>
                ) : null
            ) : (
                <Card>
                    <CardHeader>
                        <CardTitle>自定义字段</CardTitle>
                        <CardDescription>
                            {readonly
                                ? "此实体没有自定义字段数据"
                                : "选择一个自定义字段模板来添加额外信息"}
                        </CardDescription>
                    </CardHeader>
                </Card>
            )}
        </div>
    );
}