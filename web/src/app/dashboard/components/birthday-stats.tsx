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
  // 获取当前月份和下个月的时间范围
  const currentMonth = new Date()
  const nextMonth = new Date()
  nextMonth.setMonth(currentMonth.getMonth() + 1)

  const currentMonthRange = getMonthRange(currentMonth)
  const nextMonthRange = getMonthRange(nextMonth)

  // 获取当前月份的生日员工数据
  const { data: currentMonthBirthdays, isLoading: isCurrentLoading } = useBirthdayEmployees(
    companyId,
    currentMonthRange.startTime,
    currentMonthRange.endTime
  )

  // 获取下个月的生日员工数据
  const { data: nextMonthBirthdays, isLoading: isNextLoading } = useBirthdayEmployees(
    companyId,
    nextMonthRange.startTime,
    nextMonthRange.endTime
  )

  // 获取月份名称
  const currentMonthName = new Intl.DateTimeFormat('zh-CN', { month: 'long' }).format(currentMonth)
  const nextMonthName = new Intl.DateTimeFormat('zh-CN', { month: 'long' }).format(nextMonth)

  // 格式化生日日期
  const formatBirthday = (timestamp: number) => {
    const date = new Date(timestamp)
    return `${date.getMonth() + 1}月${date.getDate()}日`
  }

  // 获取姓名首字母作为头像
  const getNameInitial = (name: string) => {
    return name.charAt(0).toUpperCase()
  }

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>员工生日</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="current">
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="current">
              本月 ({currentMonthBirthdays?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="next">
              下月 ({nextMonthBirthdays?.length || 0})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="current">
            <ScrollArea className="h-[280px] pr-4">
              {isCurrentLoading ? (
                <div className="flex justify-center items-center h-full">加载中...</div>
              ) : currentMonthBirthdays && currentMonthBirthdays.length > 0 ? (
                <div className="space-y-4">
                  {currentMonthBirthdays.map((employee) => (
                    <div key={employee.id} className="flex items-center gap-3 p-2 rounded hover:bg-muted/50">
                      <Avatar className="h-9 w-9">
                        <AvatarFallback>{getNameInitial(employee.name)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1 space-y-1">
                        <div className="flex justify-between">
                          <span className="font-medium">{employee.name}</span>
                          <span className="text-sm text-muted-foreground">{formatBirthday(employee.birthdate)}</span>
                        </div>
                        <div className="text-sm text-muted-foreground">{employee.department} · {employee.position}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex justify-center items-center h-full text-muted-foreground">
                  本月无员工生日
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="next">
            <ScrollArea className="h-[280px] pr-4">
              {isNextLoading ? (
                <div className="flex justify-center items-center h-full">加载中...</div>
              ) : nextMonthBirthdays && nextMonthBirthdays.length > 0 ? (
                <div className="space-y-4">
                  {nextMonthBirthdays.map((employee) => (
                    <div key={employee.id} className="flex items-center gap-3 p-2 rounded hover:bg-muted/50">
                      <Avatar className="h-9 w-9">
                        <AvatarFallback>{getNameInitial(employee.name)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1 space-y-1">
                        <div className="flex justify-between">
                          <span className="font-medium">{employee.name}</span>
                          <span className="text-sm text-muted-foreground">{formatBirthday(employee.birthdate)}</span>
                        </div>
                        <div className="text-sm text-muted-foreground">{employee.department} · {employee.position}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex justify-center items-center h-full text-muted-foreground">
                  下月无员工生日
                </div>
              )}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}