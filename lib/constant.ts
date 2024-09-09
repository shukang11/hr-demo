import { Icons } from "@/components/icons";
import { LucideIcon } from "lucide-react";
import { DEPARTMENT_APP, MEMBER_APP, QUERY_APP, SETTING_ROOT, POSITION_APP } from "./routes";

export const siteConfig = {
  title: "人员管理",
  description: "这是一个用于管理公司员工的工具",
  url: "http://localhost:3000",
  author: {
    name: "Shu Kang",
    email: "2332532718@qq.com",
    github: "https://github.com/shukang11",
  },
};

type Submenu = {
  href: string;
  label: string;
  active: boolean;
};

type Menu = {
  href: string;
  label: string;
  active: boolean;
  icon: LucideIcon;
  submenus: Submenu[];
};

type Group = {
  groupLabel: string;
  menus: Menu[];
};

export function getMenuList(pathname: string): Group[] {
  return [
    {
      groupLabel: "",
      menus: [
        {
          href: "/",
          label: "看板",
          active: pathname === "/",
          icon: Icons.layoutGrid,
          submenus: [],
        },
      ],
    },
    {
      groupLabel: "人员招聘",
      menus: [
        {
          href: "",
          label: "招聘信息",
          active: pathname.includes("/recruitment"),
          icon: Icons.squarePen,
          submenus: [
            {
              href: "/recruitment",
              label: "招聘列表",
              active: pathname.includes("/recruitment"),
            },
          ],
        },
      ],
    },
    {
      groupLabel: "公司管理",
      menus: [
        {
          href: "",
          label: "公司成员",
          active: pathname.includes(MEMBER_APP.root),
          icon: Icons.squarePen,
          submenus: [
            {
              href: MEMBER_APP.root,
              label: "人员列表",
              active: pathname.includes(MEMBER_APP.root),
            },
          ],
        },
        {
          href: "",
          label: "公司部门",
          active: pathname.includes(DEPARTMENT_APP.root),
          icon: Icons.squarePen,
          submenus: [
            {
              href: DEPARTMENT_APP.root,
              label: "部门列表",
              active: pathname.includes(DEPARTMENT_APP.root),
            },
          ],
        },
        {
          href: "",
          label: "公司职位",
          active: pathname.includes(POSITION_APP.root),
          icon: Icons.squarePen,
          submenus: [
            {
              href: POSITION_APP.root,
              label: "职位列表",
              active: pathname.includes(POSITION_APP.root),
            },
          ],
        },
      ],
    },
    {
      groupLabel: "数据查询",
      menus: [
        {
          href: "",
          label: "数据查询",
          active: pathname.includes(QUERY_APP.root),
          icon: Icons.squarePen,
          submenus: [
            {
              href: QUERY_APP.member,
              label: "成员查询",
              active: pathname.includes(QUERY_APP.member),
            },
            {
              href: QUERY_APP.retention,
              label: "留存情况",
              active: pathname.includes(QUERY_APP.retention),
            },
          ],
        },
      ],
    },
    {
      groupLabel: "",
      menus: [
        {
          href: SETTING_ROOT,
          label: "设置",
          active: pathname.includes(QUERY_APP.root),
          icon: Icons.squarePen,
          submenus: [],
        },
      ],
    },
  ];
}

export const Service_APP = {
  setting_path: "./setting.dat",
};
