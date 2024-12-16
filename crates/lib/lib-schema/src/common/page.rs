use serde::{Deserialize, Serialize};

/// 分页参数
#[derive(Debug, Serialize, Deserialize)]
pub struct PageParams {
    /// 页码，从1开始
    pub page: u64,
    /// 每页数量
    pub limit: u64,
}

impl PageParams {
    pub fn new(page: u64, limit: u64) -> Self {
        let page = if page < 1 { 1 } else { page };
        let limit = if limit < 1 {
            1
        } else if limit > 100 {
            100
        } else {
            limit
        };
        Self { page, limit }
    }

    pub fn get_limit(&self) -> u64 {
        self.limit
    }

    pub fn get_offset(&self) -> u64 {
        (self.page - 1) * self.limit
    }
}

/// 分页结果
#[derive(Debug, Serialize, Deserialize)]
pub struct PageResult<T> {
    /// 当前页数据
    pub items: Vec<T>,
    /// 总记录数
    pub total: u64,
    /// 当前页码
    pub page: u64,
    /// 每页数量
    pub limit: u64,
    /// 总页数
    pub total_pages: u64,
}

impl<T> PageResult<T> {
    pub fn new(items: Vec<T>, total: u64, page_params: &PageParams) -> Self {
        let total_pages = (total + page_params.limit - 1) / page_params.limit;

        Self {
            items,
            total,
            page: page_params.page,
            limit: page_params.limit,
            total_pages,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_page_params() {
        // 测试正常参数
        let params = PageParams::new(2, 20);
        assert_eq!(params.page, 2);
        assert_eq!(params.limit, 20);
        assert_eq!(params.get_limit(), 20);
        assert_eq!(params.get_offset(), 20);

        // 测试页码小于1
        let params = PageParams::new(0, 20);
        assert_eq!(params.page, 1);
        assert_eq!(params.get_offset(), 0);
        
        // 测试每页记录数小于1
        let params = PageParams::new(1, 0);
        assert_eq!(params.limit, 1);

        // 测试每页记录数超过最大值
        let params = PageParams::new(1, 200);
        assert_eq!(params.limit, 100);
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
        assert_eq!(result.limit, 10);
        assert_eq!(result.total_pages, 3);
    }
}
