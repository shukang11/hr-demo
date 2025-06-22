import { AppLayout } from "@/layout/app";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { CompanyDetail as CompanyDetailType, getCompanyDetail } from "@/lib/api/company";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { BarChart } from "lucide-react";
import { SubsidiaryList } from "../components/subsidiary-list";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

export default function CompanyDetailPage() {
    const params = useParams();
    const navigate = useNavigate();
    const id = Number(params.id);
    const [companyDetail, setCompanyDetail] = useState<CompanyDetailType | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (isNaN(id)) {
            navigate("/company");
            return;
        }

        const fetchCompanyDetail = async () => {
            try {
                setIsLoading(true);
                const detail = await getCompanyDetail(id);
                setCompanyDetail(detail);
            } catch (err) {
                setError(err instanceof Error ? err : new Error("Unknown error"));
            } finally {
                setIsLoading(false);
            }
        };

        fetchCompanyDetail();
    }, [id, navigate]);

    if (isLoading) {
        return (
            <AppLayout
                breadcrumbs={[
                    { label: "公司管理", href: "/company" },
                    { label: "加载中..." },
                ]}
            >
                <div className="flex items-center justify-center h-[400px]">
                    <LoadingSpinner />
                </div>
            </AppLayout>
        );
    }

    if (error || !companyDetail) {
        return (
            <AppLayout
                breadcrumbs={[
                    { label: "公司管理", href: "/company" },
                    { label: "错误" },
                ]}
            >
                <div className="rounded-xl bg-muted/50 p-4 text-center">
                    <p className="text-red-500">加载公司详情失败</p>
                </div>
            </AppLayout>
        );
    }

    return (
        <AppLayout
            breadcrumbs={[
                { label: "公司管理", href: "/company" },
                { label: companyDetail.name },
            ]}
        >
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-semibold">{companyDetail.name}</h2>
                <div className="flex gap-2">
                    {companyDetail.subsidiaries && companyDetail.subsidiaries.length > 0 && (
                        <Button
                            variant="default"
                            size="sm"
                            onClick={() => navigate(`/dashboard/group-view/${companyDetail.id}`)}
                        >
                            <BarChart className="h-4 w-4 mr-2" />
                            集团数据视图
                        </Button>
                    )}
                </div>
            </div>

            <div className="rounded-xl bg-muted/50 p-4">
                <Tabs defaultValue="info" className="w-full">
                    <TabsList>
                        <TabsTrigger value="info">基本信息</TabsTrigger>
                        <TabsTrigger value="subsidiaries">子公司管理</TabsTrigger>
                    </TabsList>
                    <TabsContent value="info" className="mt-4">
                        <div className="bg-card rounded-md shadow p-6 dark:border border-border">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                <div>
                                    <h3 className="text-sm font-medium text-muted-foreground mb-2">公司描述</h3>
                                    <p className="text-sm leading-relaxed">{companyDetail.description || '暂无描述'}</p>
                                </div>
                                <div>
                                    <h3 className="text-sm font-medium text-muted-foreground mb-2">父公司</h3>
                                    <p className="text-sm">{companyDetail.parent_company ? companyDetail.parent_company.name : '无（为集团主公司）'}</p>
                                </div>
                                <div>
                                    <h3 className="text-sm font-medium text-muted-foreground mb-2">创建时间</h3>
                                    <p className="text-sm">{companyDetail.created_at ? new Date(companyDetail.created_at).toLocaleString('zh-CN') : '---'}</p>
                                </div>
                                <div>
                                    <h3 className="text-sm font-medium text-muted-foreground mb-2">子公司数量</h3>
                                    <p className="text-sm">{companyDetail.subsidiaries?.length || 0} 家</p>
                                </div>
                            </div>

                            {companyDetail.extra_value && (
                                <div>
                                    <h3 className="text-lg font-medium mb-2">额外信息</h3>
                                    <pre className="bg-muted dark:bg-muted/30 p-4 rounded-md overflow-x-auto">
                                        {JSON.stringify(companyDetail.extra_value, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                    </TabsContent>
                    <TabsContent value="subsidiaries" className="mt-4">
                        <SubsidiaryList companyId={companyDetail.id} />
                    </TabsContent>
                </Tabs>
            </div>
        </AppLayout>
    );
}
