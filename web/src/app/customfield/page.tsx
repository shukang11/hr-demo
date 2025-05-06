/**
 * 自定义字段管理页面
 * 
 * 提供自定义字段模板的管理功能，包括创建、编辑、克隆和删除模板。
 */
import { AppLayout } from "@/layout/app";
import { SchemaList } from "./components/schema-list";
import { SchemaEditor } from "./components/schema-editor";
import { useState } from "react";
import { JsonSchemaSchema, JsonSchemaClone, cloneJsonSchema } from "@/lib/api/customfield";
import { useToast } from "@/hooks/use-toast";
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

export default function CustomFieldPage() {
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

    const { toast } = useToast();

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
        setCloneCompanyId("");
        setIsCloneDialogOpen(true);
    };

    // 确认克隆
    const handleConfirmClone = async () => {
        if (!cloneSource) return;

        try {
            setCloneLoading(true);

            const cloneData: JsonSchemaClone = {
                source_schema_id: cloneSource.id,
                target_company_id: cloneCompanyId ? parseInt(cloneCompanyId) : 0,
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
            toast({
                title: "错误",
                description: "克隆自定义字段模板失败",
                variant: "destructive",
            });
        } finally {
            setCloneLoading(false);
        }
    };

    // 编辑器关闭后的处理
    const handleEditorClose = () => {
        setIsEditorOpen(false);
        setCurrentSchema(null);
    };

    return (
        <AppLayout
            breadcrumbs={[
                { label: "系统管理", href: "/settings" },
                { label: "自定义字段管理", href: "/customfield" },
            ]}
        >
            <div className="rounded-xl bg-muted/50 p-4">
                <SchemaList
                    onCreateSchema={handleCreateSchema}
                    onEditSchema={handleEditSchema}
                    onCloneSchema={handleCloneSchema}
                />
            </div>

            {/* Schema编辑器对话框 */}
            <SchemaEditor
                open={isEditorOpen}
                onOpenChange={setIsEditorOpen}
                schema={currentSchema}
                defaultEntityType={defaultEntityType}
                onSuccess={handleEditorClose}
            />

            {/* 克隆对话框 */}
            <Dialog open={isCloneDialogOpen} onOpenChange={setIsCloneDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>克隆自定义字段模板</DialogTitle>
                        <DialogDescription>
                            将现有模板克隆到指定公司。克隆后的模板是一个完全独立的副本。
                        </DialogDescription>
                    </DialogHeader>

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

                        <div className="space-y-2">
                            <Label htmlFor="clone-company">目标公司ID (可选)</Label>
                            <Input
                                id="clone-company"
                                type="number"
                                value={cloneCompanyId}
                                onChange={(e) => setCloneCompanyId(e.target.value)}
                                placeholder="留空表示创建通用模板"
                            />
                        </div>
                    </div>

                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => setIsCloneDialogOpen(false)}
                            disabled={cloneLoading}
                        >
                            取消
                        </Button>
                        <Button onClick={handleConfirmClone} disabled={cloneLoading || !cloneName}>
                            {cloneLoading ? "处理中..." : "确认克隆"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </AppLayout>
    );
}