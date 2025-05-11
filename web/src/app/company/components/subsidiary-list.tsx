import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PlusCircle, ExternalLink } from "lucide-react"
import { useState } from "react"
import { CompanyForm } from "./company-form"
import { Company, CompanyDetail, SubsidiaryInfo, useCompanyDetail, useSubsidiaries } from "@/lib/api/company"
import { Link } from "react-router-dom"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from "@/components/ui/table"
import { useToast } from "@/hooks/use-toast"

interface SubsidiaryListProps {
    companyId: number
}

export function SubsidiaryList({ companyId }: SubsidiaryListProps) {
    const [isSubsidiaryFormOpen, setIsSubsidiaryFormOpen] = useState(false)
    const { data: companyDetail, error, isLoading, mutate } = useCompanyDetail(companyId)
    const { toast } = useToast()

    const handleSubsidiaryAdded = () => {
        setIsSubsidiaryFormOpen(false)
        toast({
            title: "成功",
            description: "子公司添加成功",
        })
        mutate() // 刷新数据
    }

    if (isLoading) {
        return <LoadingSpinner />
    }

    if (error) {
        return <div className="text-red-500">加载子公司列表失败</div>
    }

    const subsidiaries = companyDetail?.subsidiaries || []

    return (
        <Card>
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle>子公司列表</CardTitle>
                        <CardDescription>管理 {companyDetail?.name} 的子公司</CardDescription>
                    </div>
                    <Button onClick={() => setIsSubsidiaryFormOpen(true)} size="sm" className="mt-0">
                        <PlusCircle className="mr-2 h-4 w-4" />
                        添加子公司
                    </Button>
                </div>
            </CardHeader>
            <CardContent>
                {subsidiaries.length === 0 ? (
                    <p className="text-center text-muted-foreground py-6">暂无子公司</p>
                ) : (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>ID</TableHead>
                                <TableHead>公司名称</TableHead>
                                <TableHead className="text-right">操作</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {subsidiaries.map((subsidiary) => (
                                <TableRow key={subsidiary.id}>
                                    <TableCell>{subsidiary.id}</TableCell>
                                    <TableCell>{subsidiary.name}</TableCell>
                                    <TableCell className="text-right">
                                        <Link to={`/company/${subsidiary.id}`}>
                                            <Button variant="link" size="sm">
                                                <ExternalLink className="h-4 w-4 mr-1" />
                                                查看详情
                                            </Button>
                                        </Link>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
            </CardContent>

            {/* 子公司表单对话框 */}
            {isSubsidiaryFormOpen && (
                <CompanyForm
                    open={isSubsidiaryFormOpen}
                    onOpenChange={setIsSubsidiaryFormOpen}
                    onSuccess={handleSubsidiaryAdded}
                    initialData={{ parent_id: companyId } as Company}
                />
            )}
        </Card>
    )
}
