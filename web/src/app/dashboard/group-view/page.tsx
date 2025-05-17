'use client'

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

// UI组件
import { Card, CardHeader, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download, RefreshCw } from "lucide-react";

// 自定义组件
import { SubsidiarySelector } from "../components/subsidiary-selector";
import { OverviewStats } from "../components/overview-stats";
import { RecruitmentStats } from "../components/recruitment-stats";
import { OrganizationStats } from "../components/organization-stats";
import { BirthdayStats } from "../components/birthday-stats";

// API 和 Store
import { useCompanyDetail, useSubsidiaries } from "@/lib/api/company";
import { useSubsidiariesStats } from "@/lib/api/dashboard";

export default function GroupDashboardPage() {
    const params = useParams();
    const navigate = useNavigate();
    const [selectedSubsidiaries, setSelectedSubsidiaries] = useState<number[]>([]);

    // 转换parentId为数字
    const parentIdNum = Number(params.parentId);

    // 获取父公司详情和子公司列表
    const { data: parentCompany, isLoading: isLoadingParent, error: parentError } = useCompanyDetail(parentIdNum);
    const { data: subsidiaries, isLoading: isLoadingSubsidiaries, error: subsidiariesError } = useSubsidiaries(parentIdNum);

    // 获取聚合数据
    const { data: stats, isLoading: isLoadingStats, mutate: refetchStats, error: statsError } = useSubsidiariesStats(
        parentIdNum,
        selectedSubsidiaries
    );

    // 初始化默认选中所有子公司
    useEffect(() => {
        if (subsidiaries && subsidiaries.length > 0 && selectedSubsidiaries.length === 0) {
            const allIds = subsidiaries.map((sub: { id: number }) => sub.id);
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

    // 刷新数据
    const handleRefresh = () => {
        try {
            refetchStats();
        } catch (error) {
            console.error("刷新数据失败:", error);
        }
    };

    // 导出数据
    const handleExport = () => {
        // 实现导出功能...
        alert("导出功能将在后续版本实现");
    };

    // 加载状态
    const isLoading = isLoadingParent || isLoadingSubsidiaries || isLoadingStats;

    // 错误处理
    const hasError = parentError || subsidiariesError || statsError;
    if (hasError) {
        return (
            <div className="p-4">
                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" onClick={handleBack}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <h1 className="text-xl font-bold">数据加载错误</h1>
                </div>
                <Card className="mt-4">
                    <CardHeader>
                        <CardDescription className="text-destructive">
                            加载数据时发生错误，请尝试刷新页面或稍后再试
                        </CardDescription>
                    </CardHeader>
                </Card>
            </div>
        );
    }

    return (
        <div className="p-4 space-y-4">
            <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" onClick={handleBack}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <h1 className="text-xl font-bold">
                        {parentCompany?.name || '加载中...'} - 集团数据看板
                    </h1>
                </div>

                <div className="flex items-center gap-2">
                    {/* 子公司选择器 */}
                    {parentCompany && subsidiaries && (
                        <SubsidiarySelector
                            parentCompany={{ id: parentIdNum, name: parentCompany.name }}
                            subsidiaries={subsidiaries.map((sub: { id: number, name: string }) => ({ id: sub.id, name: sub.name }))}
                            selectedIds={selectedSubsidiaries}
                            onChange={handleSubsidiaryChange}
                            className="w-[300px]"
                        />
                    )}

                    <Button variant="outline" size="icon" onClick={handleRefresh} disabled={isLoading}>
                        <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button variant="outline" size="icon" onClick={handleExport}>
                        <Download className="h-4 w-4" />
                    </Button>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardDescription>
                        {selectedSubsidiaries.length === 0
                            ? "未选择任何公司"
                            : `数据统计范围：已选择 ${selectedSubsidiaries.length} 家公司${selectedSubsidiaries.includes(parentIdNum) ? " (含母公司)" : ""}`}
                    </CardDescription>
                </CardHeader>
            </Card>

            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList className="grid grid-cols-4 max-w-[600px]">
                    <TabsTrigger value="overview">员工概览</TabsTrigger>
                    <TabsTrigger value="recruitment">招聘情况</TabsTrigger>
                    <TabsTrigger value="organization">组织发展</TabsTrigger>
                    <TabsTrigger value="birthday">员工生日</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    {stats && <OverviewStats data={stats} compact={true} />}
                </TabsContent>

                <TabsContent value="recruitment" className="space-y-4">
                    {stats && (
                        <RecruitmentStats
                            candidateStatusDistribution={stats.candidateStatusDistribution || []}
                            monthlyInterviews={stats.monthlyInterviews || 0}
                            conversionRate={stats.conversionRate || 0}
                            compact={true}
                        />
                    )}
                </TabsContent>

                <TabsContent value="organization" className="space-y-4">
                    {stats && (
                        <OrganizationStats
                            employeeGrowthTrend={stats.employeeGrowthTrend || []}
                            departmentGrowthTrend={stats.departmentGrowthTrend || []}
                            positionDistribution={stats.positionDistribution || []}
                            tenureDistribution={stats.tenureDistribution || []}
                        />
                    )}
                </TabsContent>

                <TabsContent value="birthday" className="space-y-4">
                    {selectedSubsidiaries.map(companyId => (
                        <BirthdayStats key={companyId} companyId={companyId} />
                    ))}
                </TabsContent>
            </Tabs>
        </div>
    );
}
