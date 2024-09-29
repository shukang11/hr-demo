function path(root: string, sublink: string) {
  return `${root}${sublink}`;
}

const MEMBER_ROOT = "/member"; // 成员根路径

export const MEMBER_APP = {
  root: MEMBER_ROOT, // 成员应用根路径
  insert: path(MEMBER_ROOT, "/insert"), // 成员插入路径
  import: path(MEMBER_ROOT, "/import"), // 成员导入路径
};

const DEPARTMENT_ROOT = "/department"; // 部门根路径

export const DEPARTMENT_APP = {
  root: DEPARTMENT_ROOT, // 部门应用根路径
  insert: path(DEPARTMENT_ROOT, "/insert"), // 部门插入路径
};

const QUERY_ROOT = "/query"; // 查询根路径

export const QUERY_APP = {
  root: QUERY_ROOT, // 查询应用根路径
  member: path(QUERY_ROOT, "/employee"), // 成员查询路径
  retention: path(QUERY_ROOT, "/retention"), // 保留查询路径
};

const POSITION_ROOT = "/position"; // 职位根路径

export const POSITION_APP = {
  root: POSITION_ROOT, // 职位应用根路径
  insert: path(POSITION_ROOT, "/insert"), // 职位插入路径
};

export const ALERT_APP = {

};


export const MAIN_APP = {
  HOME: "/", // 主页路径
  member: MEMBER_APP, // 成员应用
  department: DEPARTMENT_APP, // 部门应用
  query: QUERY_APP, // 查询应用
  position: POSITION_APP, // 职位应用
};

// 设置页面
export const SETTING_ROOT = "/setting"; // 设置根路径