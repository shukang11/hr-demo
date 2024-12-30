import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * 将日期转换为时间戳（毫秒）
 * @param date 日期字符串或 Date 对象
 * @returns 时间戳或 null
 */
export function dateToTimestamp(date: string | Date | null | undefined): number | null {
  if (!date) return null;
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.getTime();
}

/**
 * 将时间戳转换为日期字符串
 * @param timestamp 时间戳（毫秒）
 * @returns 日期字符串 (YYYY-MM-DD)
 */
export function timestampToDateString(timestamp: number | null | undefined): string {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toISOString().split('T')[0];
}

/**
 * 获取指定月份的时间范围
 * @param date 日期对象，默认为当前日期
 * @returns 月份的起止时间戳
 */
export function getMonthRange(date: Date = new Date()): { startTime: number; endTime: number } {
  const year = date.getFullYear()
  const month = date.getMonth()
  
  const startTime = new Date(year, month, 1).getTime()
  const endTime = new Date(year, month + 1, 0, 23, 59, 59, 999).getTime()
  
  return { startTime, endTime }
}

/**
 * 获取指定日期的时间范围（当天）
 * @param date 日期对象，默认为当前日期
 * @returns 当天的起止时间戳
 */
export function getDateRange(date: Date = new Date()): { startTime: number; endTime: number } {
  const year = date.getFullYear()
  const month = date.getMonth()
  const day = date.getDate()
  
  const startTime = new Date(year, month, day).getTime()
  const endTime = new Date(year, month, day, 23, 59, 59, 999).getTime()
  
  return { startTime, endTime }
}

/**
 * 获取跨年的时间范围
 * @param startMonth 开始月份（1-12）
 * @param startDay 开始日期
 * @param endMonth 结束月份（1-12）
 * @param endDay 结束日期
 * @param baseDate 基准日期，用于确定年份，默认为当前日期
 * @returns 时间范围的起止时间戳
 */
export function getCrossYearRange(
  startMonth: number,
  startDay: number,
  endMonth: number,
  endDay: number,
  baseDate: Date = new Date()
): { startTime: number; endTime: number } {
  const year = baseDate.getFullYear()
  
  // 如果结束月份小于开始月份，说明跨年了，结束年份需要加1
  const endYear = endMonth < startMonth ? year + 1 : year
  
  const startTime = new Date(year, startMonth - 1, startDay).getTime()
  const endTime = new Date(endYear, endMonth - 1, endDay, 23, 59, 59, 999).getTime()
  
  return { startTime, endTime }
}