import { useCallback, useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { useCompanyStore } from "@/hooks/use-company-store"
import {
  Position,
  deletePosition,
  usePositions,
  usePositionSearch
} from "@/lib/api/position"
import { PositionForm } from "./position-form"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

export function PositionList() {
  const { toast } = useToast()
  const [keyword, setKeyword] = useState("")
  const [showForm, setShowForm] = useState(false)
  const [editingPosition, setEditingPosition] = useState<Position | null>(null)
  const { currentCompany } = useCompanyStore()
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
  })

  const { data: positionData, mutate: mutatePositions } = usePositions(
    currentCompany?.id,
    pagination
  )

  const { data: searchData, mutate: mutateSearch } = usePositionSearch(
    currentCompany?.id,
    keyword,
    pagination
  )

  const positions = keyword ? searchData?.items : positionData?.items
  const totalPages = keyword ? searchData?.total_pages : positionData?.total_pages
  const isLoading = !positions

  const handleSearch = useCallback(
    (value: string) => {
      setKeyword(value)
      setPagination(prev => ({ ...prev, page: 1 }))
    },
    []
  )

  const handleEdit = useCallback((position: Position) => {
    setEditingPosition(position)
    setShowForm(true)
  }, [])

  const handleDelete = useCallback(async (id: number) => {
    try {
      await deletePosition(id)
      toast({
        title: "成功",
        description: "删除职位成功",
      })
      mutatePositions()
      mutateSearch()
    } catch (error) {
      console.error("Failed to delete position:", error)
      toast({
        variant: "destructive",
        title: "错误",
        description: "删除职位失败",
      })
    }
  }, [mutatePositions, mutateSearch, toast])

  const handleFormClose = useCallback(() => {
    setShowForm(false)
    setEditingPosition(null)
    mutatePositions()
    mutateSearch()
  }, [mutatePositions, mutateSearch])

  const handlePageChange = useCallback((newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }))
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Input
            placeholder="搜索职位..."
            value={keyword}
            onChange={(e) => handleSearch(e.target.value)}
            className="h-8 w-[150px] lg:w-[250px]"
          />
        </div>
        <Button onClick={() => setShowForm(true)}>新增职位</Button>
      </div>

      <div className="rounded-md border">
        {isLoading ? (
          <div className="flex justify-center p-8">
            <LoadingSpinner />
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>职位名称</TableHead>
                <TableHead>备注</TableHead>
                <TableHead>创建时间</TableHead>
                <TableHead>更新时间</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {positions?.map((position) => (
                <TableRow key={position.id}>
                  <TableCell>{position.name}</TableCell>
                  <TableCell>{position.remark || "-"}</TableCell>
                  <TableCell>{position.created_at ? new Date(position.created_at).toLocaleString() : "-"}</TableCell>
                  <TableCell>{position.updated_at ? new Date(position.updated_at).toLocaleString() : "-"}</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      className="h-8 w-8 p-0"
                      onClick={() => handleEdit(position)}
                    >
                      编辑
                    </Button>
                    <Button
                      variant="ghost"
                      className="h-8 w-8 p-0"
                      onClick={() => handleDelete(position.id)}
                    >
                      删除
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      {totalPages && totalPages > 1 && (
        <div className="flex justify-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePageChange(pagination.page - 1)}
            disabled={pagination.page <= 1}
          >
            上一页
          </Button>
          <div className="flex items-center space-x-1">
            <span>第 {pagination.page} 页</span>
            <span>/</span>
            <span>共 {totalPages} 页</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePageChange(pagination.page + 1)}
            disabled={pagination.page >= totalPages}
          >
            下一页
          </Button>
        </div>
      )}

      <PositionForm
        open={showForm}
        position={editingPosition}
        onClose={handleFormClose}
      />
    </div>
  )
}