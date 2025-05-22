"use client";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppLayout } from "@/layout/app";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CustomFieldEditor } from "@/components/customfield";
import { ArrowLeft, CalendarIcon, HomeIcon, MailIcon, PhoneIcon, UserIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { timestampToDateString } from "@/lib/utils";
import { getEmployeeById } from "@/lib/api/employee";
import { EmployeePositionHistory } from "./components/position-history";
import { Link } from "react-router-dom";

interface EmployeeDetailProps {
    employeeId: number;
}

export default function EmployeeDetail({ employeeId }: EmployeeDetailProps) {
    const [employee, setEmployee] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();
    const navigate = useNavigate();

    // 获取员工信息
    useEffect(() => {
        async function fetchEmployeeData() {
            try {
                setLoading(true);
                const data = await getEmployeeById(employeeId);
                setEmployee(data);
            } catch (error) {
                console.error("Failed to load employee:", error);
                toast({
                    variant: "destructive",
                    title: "加载失败",
                    description: "无法获取员工信息"
                });
            } finally {
                setLoading(false);
            }
        }

        fetchEmployeeData();
    }, [employeeId, toast]);

    // 加载中状态
    if (loading) {
        return (
            <AppLayout
                breadcrumbs={[
                    { label: "员工管理", href: "/employee" },
                    { label: "详情加载中..." }
                ]}
            >
                <div className="flex items-center justify-center h-[60vh]">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                        <p className="mt-4 text-muted-foreground">加载员工信息...</p>
                    </div>
                </div>
            </AppLayout>
        );
    }

    // 加载失败
    if (!employee) {
        return (
            <AppLayout
                breadcrumbs={[
                    { label: "员工管理", href: "/employee" },
                    { label: "详情" }
                ]}
            >
                <div className="flex flex-col items-center justify-center h-[60vh]">
                    <h1 className="text-2xl font-bold text-destructive">加载失败</h1>
                    <p className="text-muted-foreground mb-6">无法加载员工信息，请稍后重试</p>
                    <Link to="/employee">
                        <Button>返回员工列表</Button>
                    </Link>
                </div>
            </AppLayout>
        );
    }

    // 渲染员工详情
    return (
        <AppLayout
            breadcrumbs={[
                { label: "员工管理", href: "/employee" },
                { label: employee.name, href: `/employee/${employee.id}` },
                { label: "详情" }
            ]}
        >
            <div className="container mx-auto py-6">
                <div className="flex items-center justify-between mb-4">
                    <Link to="/employee">
                        <Button variant="ghost" className="flex items-center gap-2">
                            <ArrowLeft className="h-4 w-4" />
                            返回员工列表
                        </Button>
                    </Link>

                    <div className="flex items-center gap-2">
                        <Link to={`/employee/${employee.id}/edit`}>
                            <Button variant="outline">编辑员工</Button>
                        </Link>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* 员工基本信息 */}
                    <Card className="md:col-span-2">
                        <CardHeader>
                            <CardTitle>员工基本信息</CardTitle>
                            <CardDescription>ID: {employee.id}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-1">
                                    <div className="text-sm text-muted-foreground">姓名</div>
                                    <div className="flex items-center gap-2">
                                        <UserIcon className="h-4 w-4 text-muted-foreground" />
                                        <span>{employee.name}</span>
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <div className="text-sm text-muted-foreground">性别</div>
                                    <div>
                                        {employee.gender === "Male"
                                            ? "男"
                                            : employee.gender === "Female"
                                                ? "女"
                                                : "未知"}
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <div className="text-sm text-muted-foreground">电子邮件</div>
                                    <div className="flex items-center gap-2">
                                        <MailIcon className="h-4 w-4 text-muted-foreground" />
                                        <span>{employee.email || "未设置"}</span>
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <div className="text-sm text-muted-foreground">联系电话</div>
                                    <div className="flex items-center gap-2">
                                        <PhoneIcon className="h-4 w-4 text-muted-foreground" />
                                        <span>{employee.phone || "未设置"}</span>
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <div className="text-sm text-muted-foreground">出生日期</div>
                                    <div className="flex items-center gap-2">
                                        <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                                        <span>{employee.birthdate ? timestampToDateString(employee.birthdate) : "未设置"}</span>
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <div className="text-sm text-muted-foreground">地址</div>
                                    <div className="flex items-center gap-2">
                                        <HomeIcon className="h-4 w-4 text-muted-foreground" />
                                        <span>{employee.address || "未设置"}</span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* 员工自定义字段 */}
                    <Card className="md:col-span-1">
                        <CardHeader>
                            <CardTitle>自定义字段</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {employee.extra_schema_id ? (
                                <CustomFieldEditor
                                    entityType="employee"
                                    entityId={employee.id}
                                    companyId={employee.company_id}
                                    schemaId={employee.extra_schema_id}
                                    formData={employee.extra_value || undefined}
                                    readonly={true}
                                />
                            ) : (
                                <div className="text-muted-foreground text-center py-6">
                                    此员工没有自定义字段数据
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                <Tabs defaultValue="positions" className="mt-6">
                    <TabsList>
                        <TabsTrigger value="positions">职位历史</TabsTrigger>
                        <TabsTrigger value="attachments">附件文档</TabsTrigger>
                    </TabsList>
                    <TabsContent value="positions" className="mt-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>职位历史记录</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <EmployeePositionHistory employeeId={employee.id} />
                            </CardContent>
                        </Card>
                    </TabsContent>
                    <TabsContent value="attachments" className="mt-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>附件文档</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-muted-foreground text-center py-6">
                                    暂无附件文档
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </AppLayout>
    );
}
