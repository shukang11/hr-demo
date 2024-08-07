import Link from "next/link";
import { SignInForm } from "./signin-form";

export default function Page() {
    return (
        <>
            <div className="flex flex-col space-y-2 text-center">
                <h1 className="text-2xl font-semibold tracking-tight">
                    账户登录
                </h1>
                <p className="text-sm text-muted-foreground">
                    请输入账号密码登录
                </p>
            </div>
            <>
                <SignInForm />
            </>
            <p className="px-8 text-center text-sm text-muted-foreground">
                点击“继续”即表示您同意我们的{" "}
                <Link
                    href="/terms"
                    className="underline underline-offset-4 hover:text-primary"
                >
                    服务条款
                </Link>{" "}
                和{" "}
                <Link
                    href="/privacy"
                    className="underline underline-offset-4 hover:text-primary"
                >
                    隐私政策
                </Link>
                .
            </p>
        </>
    );
}