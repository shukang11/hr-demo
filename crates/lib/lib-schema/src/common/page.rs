use serde::{Deserialize, Serialize};

/// 分页请求参数
#[derive(Debug, Deserialize, Clone)]
pub struct PageParams {
    /// 页码，从1开始
    #[serde(default = "default_page")]
    pub page: u64,
    /// 每页记录数
    #[serde(default = "default_page_size")]
    pub page_size: u64,
}

/// 分页响应结果
#[derive(Debug, Serialize)]
pub struct PageResult<T> {
    /// 当前页数据
    pub items: Vec<T>,
    /// 总记录数
    pub total: u64,
    /// 当前页码
    pub page: u64,
    /// 每页记录数
    pub page_size: u64,
    /// 总页数
    pub total_pages: u64,
}

impl PageParams {
    /// 创建新的分页参数
    pub fn new(page: u64, page_size: u64) -> Self {
        Self {
            page: if page < 1 { 1 } else { page },
            page_size: if page_size < 1 { 
                default_page_size()
            } else { 
                page_size.min(max_page_size()) 
            },
        }
    }

    /// 获取偏移量
    pub fn get_offset(&self) -> u64 {
        (self.page - 1) * self.page_size
    }

    /// 获取限制数
    pub fn get_limit(&self) -> u64 {
        self.page_size
    }
}

impl<T> PageResult<T> {
    /// 创建新的分页结果
    pub fn new(items: Vec<T>, total: u64, params: &PageParams) -> Self {
        let total_pages = (total + params.page_size - 1) / params.page_size;
        Self {
            items,
            total,
            page: params.page,
            page_size: params.page_size,
            total_pages,
        }
    }
}

/// 默认页码
fn default_page() -> u64 {
    1
}

/// 默认每页记录数
fn default_page_size() -> u64 {
    10
}

/// 最大每页记录数
fn max_page_size() -> u64 {
    100
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_page_params() {
        // 测试正常参数
        let params = PageParams::new(2, 20);
        assert_eq!(params.page, 2);
        assert_eq!(params.page_size, 20);
        assert_eq!(params.get_offset(), 20);
        assert_eq!(params.get_limit(), 20);

        // 测试页码小于1
        let params = PageParams::new(0, 20);
        assert_eq!(params.page, 1);
        
        // 测试每页记录数小于1
        let params = PageParams::new(1, 0);
        assert_eq!(params.page_size, default_page_size());

        // 测试每页记录数超过最大值
        let params = PageParams::new(1, 200);
        assert_eq!(params.page_size, max_page_size());
    }

    #[test]
    fn test_page_result() {
        let params = PageParams::new(2, 10);
        let items = vec![1, 2, 3];
        let total = 25;

        let result = PageResult::new(items.clone(), total, &params);
        assert_eq!(result.items, items);
        assert_eq!(result.total, total);
        assert_eq!(result.page, 2);
        assert_eq!(result.page_size, 10);
        assert_eq!(result.total_pages, 3);
    }
}
