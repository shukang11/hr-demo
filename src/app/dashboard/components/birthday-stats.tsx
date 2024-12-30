import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useBirthdayEmployees } from "@/lib/api/dashboard"
import { getMonthRange } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface BirthdayStatsProps {
  companyId: number
}

export function BirthdayStats({ companyId }: BirthdayStatsProps) {
  // 获取本月范围
  const thisMonth = getMonthRange()
  const { data: thisMonthEmployees } = useBirthdayEmployees(
    companyId,
    thisMonth.startTime,
    thisMonth.endTime
  )

  // 获取下个月范围
  const nextMonth = getMonthRange(new Date(thisMonth.endTime + 24 * 60 * 60 * 1000))
  const { data: nextMonthEmployees } = useBirthdayEmployees(
    companyId,
    nextMonth.startTime,
    nextMonth.endTime
  )

  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle>员工生日提醒</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="this-month">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="this-month">
              本月过生日 ({thisMonthEmployees?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="next-month">
              下月过生日 ({nextMonthEmployees?.length || 0})
            </TabsTrigger>
          </TabsList>
          <TabsContent value="this-month">
            <ScrollArea className="h-[300px] pr-4">
              <div className="space-y-4 mt-4">
                {thisMonthEmployees?.map((employee) => (
                  <div
                    key={employee.id}
                    className="flex items-center gap-4 p-2 rounded-lg hover:bg-muted"
                  >
                    <Avatar>
                      <AvatarFallback>
                        {employee.name.slice(0, 2)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {employee.name}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {employee.department} · {employee.position}
                      </p>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(employee.birthdate).getDate()}日
                    </div>
                  </div>
                ))}
                {thisMonthEmployees?.length === 0 && (
                  <div className="text-center text-muted-foreground py-8">
                    本月暂无员工过生日
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
          <TabsContent value="next-month">
            <ScrollArea className="h-[300px] pr-4">
              <div className="space-y-4 mt-4">
                {nextMonthEmployees?.map((employee) => (
                  <div
                    key={employee.id}
                    className="flex items-center gap-4 p-2 rounded-lg hover:bg-muted"
                  >
                    <Avatar>
                      <AvatarFallback>
                        {employee.name.slice(0, 2)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {employee.name}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {employee.department} · {employee.position}
                      </p>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(employee.birthdate).getDate()}日
                    </div>
                  </div>
                ))}
                {nextMonthEmployees?.length === 0 && (
                  <div className="text-center text-muted-foreground py-8">
                    下月暂无员工过生日
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
} 