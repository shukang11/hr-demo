import { useState, useEffect } from 'react';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from '@/hooks/use-auth';
import { useParams, useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ArrowLeft, BarChart, Loader2 } from 'lucide-react';
import {
    useSubsidiariesStats,
    DashboardStats
} from '@/lib/api/dashboard';
import { SubsidiarySelector } from "@/components/company/subsidiary-selector";
import {
    useCompanyDetail,
    useSubsidiaries
} from '@/lib/api/company';

// 统计图表组件导入
import { EmployeeCount } from '@/components/charts/employee-count';
import { DepartmentPie } from '@/components/charts/department-pie';
import { GenderPie } from '@/components/charts/gender-pie';
import { AgeBar } from '@/components/charts/age-bar';
import { CandidateStatus } from '@/components/charts/candidate-status';
import { MonthlyCount } from '@/components/charts/monthly-count';
import { DepartmentRecruitment } from '@/components/charts/department-recruitment';
import { EmployeeGrowth } from '@/components/charts/employee-growth';
import { PositionDistribution } from '@/components/charts/position-distribution';
import { TenureDistribution } from '@/components/charts/tenure-distribution';

export default function GroupDashboardPage() {
    const params = useParams();
    const navigate = useNavigate();
    const { toast } = useToast();
    const { user } = useAuth();
    const [selectedSubsidiaries, setSelectedSubsidiaries] = useState<number[]>([]);

    // 转换parentId为数字
    const parentIdNum = Number(params.parentId);

    // 获取父公司详情和子公司列表
    const { data: parentCompany, isLoading: isLoadingParent } = useCompanyDetail(parentIdNum);
    const { data: subsidiaries, isLoading: isLoadingSubsidiaries } = useSubsidiaries(parentIdNum);

    // 获取聚合数据
    const { data: stats, isLoading: isLoadingStats } = useSubsidiariesStats(parentIdNum, selectedSubsidiaries);

    // 初始化默认选中所有子公司
    useEffect(() => {
        if (subsidiaries && subsidiaries.length > 0 && selectedSubsidiaries.length === 0) {
            const allIds = subsidiaries.map(sub => sub.id);
            // 添加父公司ID
            setSelectedSubsidiaries([parentIdNum, ...allIds]);
        }
    }, [subsidiaries, parentIdNum, selectedSubsidiaries.length]);

    // 处理子公司选择变化
    const handleSubsidiaryChange = (ids: number[]) => {
        setSelectedSubsidiaries(ids);
    };

    // 返回按钮处理
    const handleBack = () => {
        navigate(`/company/${parentIdNum}`);
    };

    if (!user) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="p-6 space-y-4">
            <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
                <div>
                    <Button
                        variant="outline"
                        size="sm"
                        className="mb-2"
                        onClick={handleBack}
                    >
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        返回公司
                    </Button>
                    <h2 className="text-3xl font-bold tracking-tight">
                        {isLoadingParent ? (
                            <Skeleton className="h-9 w-64" />
                        ) : (
                            `${parentCompany?.name || '公司'} 集团仪表盘`
                        )}
                    </h2>
                    <p className="text-muted-foreground">
                        查看所有子公司的汇总数据和整体运营状况
                    </p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>子公司选择</CardTitle>
                    <CardDescription>
                        选择要在仪表盘中显示的公司数据
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <SubsidiarySelector
                        parentId={parentIdNum}
                        selectedIds={selectedSubsidiaries}
                        onChange={handleSubsidiaryChange}
                        includeParent={true}
                    />
                </CardContent>
            </Card>

            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="overview" className="flex items-center gap-2">
                        <BarChart className="h-4 w-4" />
                        <span>全局视图</span>
                    </TabsTrigger>
                </TabsList>
                <TabsContent value="overview" className="space-y-4">
                    {isLoadingStats ? (
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {Array.from({ length: 9 }).map((_, index) => (
                                <Card key={index}>
                                    <CardHeader className="pb-2">
                                        <Skeleton className="h-5 w-1/2" />
                                    </CardHeader>
                                    <CardContent>
                                        <Skeleton className="h-[180px] w-full" />
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    ) : stats ? (
                        <>
                            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>员工总数</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <EmployeeCount data={stats} />
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>部门分布</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <DepartmentPie data={stats} />
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>性别比例</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <GenderPie data={stats} />
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>年龄分布</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <AgeBar data={stats} />
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>候选人状态</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <CandidateStatus data={stats} />
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>月度面试</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <MonthlyCount
                                            count={stats.monthlyInterviews}
                                            label="面试"
                                        />
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>部门招聘 Top 5</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <DepartmentRecruitment data={stats} />
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>员工增长趋势</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <EmployeeGrowth data={stats} />
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>职位分布</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <PositionDistribution data={stats} />
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle>任职时长分布</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <TenureDistribution data={stats} />
                                    </CardContent>
                                </Card>
                            </div>
                        </>
                    ) : (
                        <Card>
                            <CardContent className="pt-6 text-center">
                                <p className="text-muted-foreground">无法加载仪表盘数据</p>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}
