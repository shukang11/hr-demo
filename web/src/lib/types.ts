export interface PageParams {
  page: number
  limit: number
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  limit: number
  total_pages: number
} 