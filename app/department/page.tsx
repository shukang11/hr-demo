'use client';

import { Button } from "@/components/ui/button";
import Container from "./list/container";
import Link from "next/link";
import { DEPARTMENT_APP } from "@/lib/routes";
import { writeFile } from "@tauri-apps/plugin-fs";
import { downloadDir } from "@tauri-apps/api/path";
import { open } from '@tauri-apps/plugin-shell';

export default function Page() {

    // 添加一个按钮，点击后下载模板文件
    const downloadTemplate = async () => {
        // 定义字段，用于生成文件
        const fields = [
            { label: '部门名称', key: 'name' },
            { label: '部门描述', key: 'description' },
        ];
        // 生成文件内容
        const csv = fields.map(f => f.label).join(',') + '\n';

        // 获取系统的下载目录
        const downloadPath = await downloadDir();
        const filePath = `${downloadPath}/department_template.csv`;

        let encoder = new TextEncoder();
        let data = encoder.encode(csv);

        // 将内容写入下载目录的指定文件中
        await writeFile(filePath, data)

        // 尝试打开目标文件夹，选中模板文件
        await open(downloadPath);
    }

    return (
        <div className="flex flex-col">
            <div className="flex justify-end mb-10 space-x-4">
                <Link href={DEPARTMENT_APP.insert}>
                    <Button>新增</Button>
                </Link>
                <Button>导出</Button>
                <Button onClick={downloadTemplate}>下载模板</Button>
            </div>
            <Container />
        </div>
    )
}