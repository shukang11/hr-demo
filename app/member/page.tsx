import { Button } from "@/components/ui/button";
import Container from "./list/container";
import Link from "next/link";
import { MEMBER_APP } from "@/lib/routes";

export default function Page() {
    return (
        <div className="flex flex-col">
            <div className="flex justify-end mb-10 space-x-4">
                <Link href={MEMBER_APP.insert}>
                    <Button>新增</Button>
                </Link>
                <Button>导出</Button>
            </div>
            <Container />
        </div>
    )
}