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