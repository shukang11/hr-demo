import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useState } from "react"
import { CompanyForm } from "./company-form"
import { Company, deleteCompany, useCompanies } from "@/lib/api/company"
import { PageParams } from "@/lib/types"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { useToast } from "@/hooks/use-toast"

export function CompanyList() {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [currentCompany, setCurrentCompany] = useState<Company | null>(null)
  const [pageParams, setPageParams] = useState<PageParams>({
    page: 1,
    limit: 10,
  })
  const { data, error, isLoading, mutate } = useCompanies(pageParams)
  const { toast } = useToast()

  const handleEdit = (company: Company) => {
    setCurrentCompany(company)
    setIsFormOpen(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm("确定要删除这个公司吗？")) {
      return
    }

    try {
      await deleteCompany(id)
      toast({
        title: "成功",
        description: "删除公司成功",
      })
      mutate() // 刷新数据
    } catch (error) {
      console.error("删除公司失败:", error)
      toast({
        title: "错误",
        description: "删除公司失败",
        variant: "destructive",
      })
    }
  }

  const handleFormClose = () => {
    setIsFormOpen(false)
    setCurrentCompany(null)
  }

  const handleFormSuccess = () => {
    handleFormClose()
    mutate() // 刷新数据
  }

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <LoadingSpinner className="mr-2" />
        加载中...
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center text-destructive">
        加载失败: {error.message}
      </div>
    )
  }

  if (!data) {
    return null
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">公司列表</h2>
        <Button onClick={() => setIsFormOpen(true)}>新建公司</Button>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>公司名称</TableHead>
            <TableHead>创建时间</TableHead>
            <TableHead>更新时间</TableHead>
            <TableHead>操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.items.map((company) => (
            <TableRow key={company.id}>
              <TableCell>{company.id}</TableCell>
              <TableCell>{company.name}</TableCell>
              <TableCell>{company.created_at ? new Date(company.created_at).toLocaleString() : '-'}</TableCell>
              <TableCell>{company.updated_at ? new Date(company.updated_at).toLocaleString() : '-'}</TableCell>
              <TableCell>
                <div className="space-x-2">
                  <Button variant="ghost" size="sm" onClick={() => handleEdit(company)}>
                    编辑
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(company.id)}
                  >
                    删除
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <CompanyForm
        open={isFormOpen}
        onOpenChange={handleFormClose}
        onSuccess={handleFormSuccess}
        initialData={currentCompany}
      />
    </div>
  )
} 