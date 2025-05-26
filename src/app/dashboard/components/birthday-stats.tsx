'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { BirthdayEmployee, useBirthdayEmployees } from "@/lib/api/dashboard"
import { CalendarDays, Gift } from "lucide-react"

interface BirthdayStatsProps {
  companyId: number
  compact?: boolean
}

// 获取月份的时间范围
function getMonthRange(date: Date) {
  const year = date.getFullYear()
  const month = date.getMonth()

  const startDate = new Date(year, month, 1)
  const endDate = new Date(year, month + 1, 0)

  return {
    startTime: startDate.getTime(),
    endTime: endDate.getTime()
  }
}

export function BirthdayStats({ companyId, compact = false }: BirthdayStatsProps) {
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

  // 计算两个日期之间的天数
  const getDaysUntilBirthday = (birthdayTimestamp: number) => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    const birthday = new Date(birthdayTimestamp)
    const birthdayThisYear = new Date(today.getFullYear(), birthday.getMonth(), birthday.getDate())

    if (birthdayThisYear < today) {
      // 如果今年的生日已经过了，计算到明年的生日
      birthdayThisYear.setFullYear(today.getFullYear() + 1)
    }

    const diffTime = Math.abs(birthdayThisYear.getTime() - today.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    return diffDays
  }

  // 显示员工生日信息
  const renderBirthdayPeople = (people: BirthdayEmployee[] | null | undefined, isLoading: boolean) => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full"></div>
        </div>
      )
    }

    if (!people || people.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
          <Gift className="h-12 w-12 mb-2 opacity-20" />
          <p>本月暂无员工生日</p>
        </div>
      )
    }

    const sortedPeople = [...people].sort((a, b) => {
      const dateA = new Date(a.birthdate)
      const dateB = new Date(b.birthdate)
      return dateA.getDate() - dateB.getDate()
    })

    return (
      <div className={`space-y-4 ${compact ? 'max-h-[240px] overflow-y-auto pr-2' : ''}`}>
        {sortedPeople.map((person) => (
          <div key={person.id} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Avatar className="h-8 w-8">
                {person.name ? (
                  <img src={person.name} alt={person.name} />
                ) : (
                  <AvatarFallback>{getNameInitial(person.name)}</AvatarFallback>
                )}
              </Avatar>
              <div>
                <p className="text-sm font-medium">{person.name}</p>
                <p className="text-xs text-muted-foreground">{person.department}</p>
              </div>
            </div>
            <div className="flex flex-col items-end">
              <Badge variant="outline" className="flex items-center gap-1">
                <CalendarDays className="h-3 w-3" />
                {formatBirthday(person.birthdate)}
              </Badge>
              {getDaysUntilBirthday(person.birthdate) === 0 ? (
                <span className="text-xs text-red-500 font-medium">今天</span>
              ) : (
                <span className="text-xs text-muted-foreground">
                  还有 {getDaysUntilBirthday(person.birthdate)} 天
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <Card className={compact ? "col-span-full" : "col-span-1"}>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Gift className="h-5 w-5" />
          员工生日
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="current">
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="current">
              {currentMonthName}
              {currentMonthBirthdays && currentMonthBirthdays.length > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {currentMonthBirthdays.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="next">
              {nextMonthName}
              {nextMonthBirthdays && nextMonthBirthdays.length > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {nextMonthBirthdays.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="current">
            {renderBirthdayPeople(currentMonthBirthdays, isCurrentLoading)}
          </TabsContent>

          <TabsContent value="next">
            {renderBirthdayPeople(nextMonthBirthdays, isNextLoading)}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}