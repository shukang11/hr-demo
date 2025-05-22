/**
 * 动态表单组件
 * 
 * 基于JSON Schema和UI Schema动态生成表单，使用React JSON Schema Form库。
 * 支持所有JSON Schema类型，能够处理复杂的嵌套结构和验证规则。
 */
import { useMemo } from 'react';
import { RJSFSchema } from '@rjsf/utils';
import validator from '@rjsf/validator-ajv8';
import Form from '@rjsf/shadcn';
import { cn } from '@/lib/utils';

export interface DynamicFormProps {
    /**
     * JSON Schema定义，描述数据结构和验证规则
     */
    schema: RJSFSchema;

    /**
     * UI Schema配置，描述UI渲染方式，可选
     */
    uiSchema?: Record<string, any>;

    /**
     * 表单数据，可选
     */
    formData?: Record<string, any>;

    /**
     * 表单提交回调函数
     */
    onSubmit?: (data: { formData: Record<string, any> }) => void;

    /**
     * 表单数据变更回调函数
     */
    onChange?: (data: { formData: Record<string, any> }) => void;

    /**
     * 是否禁用表单，默认为false
     */
    disabled?: boolean;

    /**
     * 是否只读，默认为false
     */
    readonly?: boolean;

    /**
     * 是否显示提交按钮，默认为true
     */
    showSubmitButton?: boolean;

    /**
     * 自定义CSS类名
     */
    className?: string;

    /**
     * 表单错误回调函数
     */
    onError?: (errors: any[]) => void;
}

/**
 * 动态表单组件
 * 
 * 根据提供的JSON Schema和UI Schema动态渲染表单。
 * 
 * @example
 * ```tsx
 * <DynamicForm 
 *   schema={schema}
 *   uiSchema={uiSchema}
 *   formData={initialData}
 *   onSubmit={handleSubmit}
 *   onChange={handleChange}
 * />
 * ```
 */
export function DynamicForm({
    schema,
    uiSchema,
    formData,
    onSubmit,
    onChange,
    disabled = false,
    readonly = false,
    showSubmitButton = true,
    className,
    onError,
}: DynamicFormProps) {
    // 处理提交事件
    const handleSubmit = (data: { formData: Record<string, any> }) => {
        onSubmit?.(data);
    };

    // 处理变更事件
    const handleChange = (data: any, id?: string) => {
        onChange?.({ formData: data.formData || {} });
    };

    // 处理错误事件
    const handleError = (errors: any[]) => {
        console.error('Form validation errors:', errors);
        onError?.(errors);
    };

    // 根据是否显示提交按钮，处理表单按钮
    const customButtons = useMemo(() => {
        if (!showSubmitButton) {
            return { submit: <></> };
        }
        return undefined;
    }, [showSubmitButton]);

    return (
        <div className={cn('customfield-form', className)}>
            <Form
                schema={schema}
                validator={validator}
                uiSchema={uiSchema}
                formData={formData}
                onSubmit={handleSubmit}
                onChange={handleChange}
                disabled={disabled}
                readonly={readonly}
                onError={handleError}
                customButtons={customButtons}
            />
        </div>
    );
}

/**
 * 动态表单查看组件
 * 
 * 提供只读模式查看表单数据的专用组件。
 */
export function DynamicFormViewer({
    schema,
    uiSchema,
    formData,
    className,
}: Omit<DynamicFormProps, 'onSubmit' | 'onChange' | 'disabled' | 'readonly' | 'showSubmitButton' | 'onError'>) {
    return (
        <DynamicForm
            schema={schema}
            uiSchema={uiSchema}
            formData={formData}
            readonly={true}
            showSubmitButton={false}
            className={cn('customfield-viewer', className)}
        />
    );
}