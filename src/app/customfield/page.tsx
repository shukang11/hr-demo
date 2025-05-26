/**
 * 自定义字段管理页面
 * 
 * 提供自定义字段模板的管理功能，包括创建、编辑、克隆和删除模板。
 * 公司拥有者可以管理其公司的自定义字段，并查看系统预设的字段。
 */
import { AppLayout } from "@/layout/app";
import { SchemaList } from "./components/schema-list";
import { SchemaEditor } from "./components/schema-editor";
import { useState, useEffect } from "react";
import { JsonSchemaSchema, JsonSchemaClone, cloneJsonSchema } from "@/lib/api/customfield";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/lib/auth/auth-context";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { useCompanyStore } from "@/hooks/use-company-store";

export default function CustomFieldPage() {
    // 获取当前用户信息
    const { user } = useAuth();
    const { currentCompany } = useCompanyStore();

    // 编辑器状态
    const [isEditorOpen, setIsEditorOpen] = useState(false);
    const [currentSchema, setCurrentSchema] = useState<JsonSchemaSchema | null>(null);
    const [defaultEntityType, setDefaultEntityType] = useState("Company");

    // 克隆对话框状态
    const [isCloneDialogOpen, setIsCloneDialogOpen] = useState(false);
    const [cloneSource, setCloneSource] = useState<JsonSchemaSchema | null>(null);
    const [cloneName, setCloneName] = useState("");
    const [cloneCompanyId, setCloneCompanyId] = useState<string>("");
    const [cloneLoading, setCloneLoading] = useState(false);
    const [cloneError, setCloneError] = useState<string | null>(null);

    // 当前用户公司ID
    const [currentCompanyId, setCurrentCompanyId] = useState<number | undefined>(undefined);

    const { toast } = useToast();

    // 初始化时，设置当前公司ID
    useEffect(() => {
        if (currentCompany?.id) {
            setCurrentCompanyId(currentCompany.id);
        }
    }, [currentCompany]);

    // 处理创建新Schema
    const handleCreateSchema = (entityType: string) => {
        setCurrentSchema(null);
        setDefaultEntityType(entityType);
        setIsEditorOpen(true);
    };

    // 处理编辑Schema
    const handleEditSchema = (schema: JsonSchemaSchema) => {
        setCurrentSchema(schema);
        setIsEditorOpen(true);
    };

    // 处理克隆Schema
    const handleCloneSchema = (schema: JsonSchemaSchema) => {
        setCloneSource(schema);
        setCloneName(schema.name + " (克隆)");
        // 默认克隆到当前公司
        setCloneCompanyId(currentCompanyId ? currentCompanyId.toString() : "");
        setCloneError(null);
        setIsCloneDialogOpen(true);
    };

    // 确认克隆
    const handleConfirmClone = async () => {
        if (!cloneSource) return;

        try {
            setCloneLoading(true);
            setCloneError(null);

            const cloneData: JsonSchemaClone = {
                source_schema_id: cloneSource.id,
                target_company_id: cloneCompanyId ? parseInt(cloneCompanyId) :
                    (currentCompanyId || 0),  // 默认使用当前公司ID
                name: cloneName || undefined,
            };

            await cloneJsonSchema(cloneData);
            toast({
                title: "成功",
                description: "克隆自定义字段模板成功",
            });

            setIsCloneDialogOpen(false);
            // 刷新列表（SchemaList组件会自动刷新）
        } catch (error) {
            console.error("克隆自定义字段模板失败:", error);
            setCloneError(error instanceof Error ? error.message : "克隆失败，请稍后重试");
        } finally {
            setCloneLoading(false);
        }
    };

    // 编辑器关闭后的处理
    const handleEditorClose = () => {
        setIsEditorOpen(false);
        setCurrentSchema(null);
    };

    // 生成页面标题
    const pageTitle = user?.is_admin
        ? "自定义字段管理"
        : `${user?.company_name || '公司'}自定义字段管理`;

    // 如果用户未登录或无法获取用户信息时显示错误
    if (!user) {
        return (
            <AppLayout
                breadcrumbs={[
                    { label: "系统管理", href: "/settings" },
                    { label: "自定义字段管理", href: "/customfield" },
                ]}
            >
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>无法加载用户信息</AlertTitle>
                    <AlertDescription>
                        请确保您已登录并刷新页面。如果问题持续存在，请联系系统管理员。
                    </AlertDescription>
                </Alert>
            </AppLayout>
        );
    }

    return (
        <AppLayout
            breadcrumbs={[
                { label: "系统管理", href: "/settings" },
                { label: pageTitle, href: "/customfield" },
            ]}
        >
            <div className="rounded-xl bg-muted/50 p-4">
                {/* 传递当前公司ID给SchemaList组件 */}
                <SchemaList
                    onCreateSchema={handleCreateSchema}
                    onEditSchema={handleEditSchema}
                    onCloneSchema={handleCloneSchema}
                    currentCompanyId={currentCompanyId}
                    isAdmin={user?.is_admin || false}
                />
            </div>

            {/* Schema编辑器对话框 */}
            <SchemaEditor
                open={isEditorOpen}
                onOpenChange={setIsEditorOpen}
                schema={currentSchema}
                defaultEntityType={defaultEntityType}
                onSuccess={handleEditorClose}
                defaultCompanyId={currentCompanyId}  // 传递当前公司ID
            />

            {/* 克隆对话框 */}
            <Dialog open={isCloneDialogOpen} onOpenChange={setIsCloneDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>克隆自定义字段模板</DialogTitle>
                        <DialogDescription>
                            将现有模板克隆到你的公司。克隆后的模板是一个完全独立的副本。
                        </DialogDescription>
                    </DialogHeader>

                    {cloneError && (
                        <Alert variant="destructive" className="mt-2">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>{cloneError}</AlertDescription>
                        </Alert>
                    )}

                    <div className="grid gap-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="clone-name">模板名称</Label>
                            <Input
                                id="clone-name"
                                value={cloneName}
                                onChange={(e) => setCloneName(e.target.value)}
                                placeholder="输入新的模板名称"
                            />
                        </div>

                        {user?.is_admin && (
                            <div className="space-y-2">
                                <Label htmlFor="clone-company">目标公司ID</Label>
                                <Input
                                    id="clone-company"
                                    type="number"
                                    value={cloneCompanyId}
                                    onChange={(e) => setCloneCompanyId(e.target.value)}
                                    placeholder={currentCompanyId ? `默认: ${currentCompanyId}` : "输入公司ID"}
                                />
                            </div>
                        )}
                    </div>

                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => setIsCloneDialogOpen(false)}
                            disabled={cloneLoading}
                        >
                            取消
                        </Button>
                        <Button
                            onClick={handleConfirmClone}
                            disabled={cloneLoading || !cloneName}
                        >
                            {cloneLoading ? "处理中..." : "确认克隆"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </AppLayout>
    );
}