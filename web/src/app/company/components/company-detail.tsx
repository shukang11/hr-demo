/**
 * 公司详情对话框组件
 * 
 * 显示公司的详细信息，包括基本信息和自定义字段数据
 */
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Company } from "@/lib/api/company";
import { DynamicFormViewer } from "@/components/customfield";
import { useSchema } from "@/lib/api/customfield";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";

interface CompanyDetailProps {
    /**
     * 对话框是否打开
     */
    open: boolean;

    /**
     * 对话框打开状态变化回调
     */
    onOpenChange: (open: boolean) => void;

    /**
     * 公司数据
     */
    data: Company | null;

    /**
     * 点击编辑按钮回调
     */
    onEdit?: () => void;
}

/**
 * 公司详情对话框组件
 */
export function CompanyDetail({ open, onOpenChange, data, onEdit }: CompanyDetailProps) {
    const { data: schema, isLoading } = useSchema(data?.extra_schema_id || undefined);

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-lg">
                <DialogHeader>
                    <DialogTitle>公司详情</DialogTitle>
                </DialogHeader>

                <div className="space-y-6">
                    {/* 基本信息 */}
                    <div>
                        <h3 className="text-sm font-medium mb-2">基本信息</h3>
                        <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                            <div className="text-sm text-muted-foreground">公司名称</div>
                            <div className="text-sm font-medium">{data?.name || '---'}</div>

                            <div className="text-sm text-muted-foreground">公司ID</div>
                            <div className="text-sm font-medium">{data?.id || '---'}</div>

                            <div className="text-sm text-muted-foreground">创建时间</div>
                            <div className="text-sm font-medium">
                                {data?.created_at
                                    ? new Date(data.created_at).toLocaleString()
                                    : '---'}
                            </div>

                            <div className="text-sm text-muted-foreground">更新时间</div>
                            <div className="text-sm font-medium">
                                {data?.updated_at
                                    ? new Date(data.updated_at).toLocaleString()
                                    : '---'}
                            </div>
                        </div>
                    </div>

                    <Separator />

                    {/* 自定义字段 */}
                    <div>
                        <h3 className="text-sm font-medium mb-2">自定义字段</h3>
                        {data?.extra_schema_id ? (
                            isLoading ? (
                                <Card>
                                    <CardHeader>
                                        <Skeleton className="h-4 w-[250px]" />
                                        <Skeleton className="h-4 w-[200px]" />
                                    </CardHeader>
                                    <CardContent>
                                        <Skeleton className="h-[100px] w-full" />
                                    </CardContent>
                                </Card>
                            ) : schema ? (
                                <Card>
                                    <CardHeader>
                                        <CardTitle>{schema.name}</CardTitle>
                                        {schema.remark && <CardDescription>{schema.remark}</CardDescription>}
                                    </CardHeader>
                                    <CardContent>
                                        <DynamicFormViewer
                                            schema={schema.schema as any}
                                            uiSchema={schema.ui_schema || undefined}
                                            formData={data.extra_value}
                                        />
                                    </CardContent>
                                </Card>
                            ) : (
                                <div className="text-sm text-muted-foreground py-2">
                                    无法加载自定义字段模板
                                </div>
                            )
                        ) : (
                            <div className="text-sm text-muted-foreground py-2">
                                此公司没有自定义字段数据
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex justify-end space-x-2 mt-4">
                    {onEdit && (
                        <Button
                            variant="outline"
                            onClick={() => {
                                onEdit();
                                onOpenChange(false);
                            }}
                        >
                            编辑
                        </Button>
                    )}
                    <Button onClick={() => onOpenChange(false)}>关闭</Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}