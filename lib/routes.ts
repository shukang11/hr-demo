function path(root: string, sublink: string) {
  return `${root}${sublink}`;
}

const MEMBER_ROOT = "/member";

export const MEMBER_APP = {
  root: MEMBER_ROOT,
  insert: path(MEMBER_ROOT, "/insert"),
  import: path(MEMBER_ROOT, "/import"),
};

const DEPARTMENT_ROOT = "/department";

export const DEPARTMENT_APP = {
  root: DEPARTMENT_ROOT,
  insert: path(DEPARTMENT_ROOT, "/insert"),
};

const QUERY_ROOT = "/query";

export const QUERY_APP = {
  root: QUERY_ROOT,
  member: path(QUERY_ROOT, "/employee"),
  retention: path(QUERY_ROOT, "/retention"),
};

const POSITION_ROOT = "/position";

export const POSITION_APP = {
  root: POSITION_ROOT,
  insert: path(POSITION_ROOT, "/insert"),
};

export const MAIN_APP = {
  HOME: "/",
  member: MEMBER_APP,
  department: DEPARTMENT_APP,
  query: QUERY_APP,
  position: POSITION_APP,
};

// 设置页面
export const SETTING_ROOT = "/setting";