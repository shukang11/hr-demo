'use client';

import { cn } from "@/lib/utils";
import { AccountInfo } from "@/types";
import { useRouter, useSearchParams } from "next/navigation";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { signIn, signOut } from "next-auth/react";
import { AUTHENTICATION_APP, MAIN_APP } from "@/lib/routes";

import { Form, FormField, FormItem, FormMessage } from "@/components/ui/form";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface UserSignInFormProps extends React.HTMLAttributes<HTMLDivElement> {
    user?: AccountInfo;
}

const FormSchema = z.object({
    email: z.string({
        required_error: "请输入邮箱"
    }).email({
        message: "请输入有效的邮箱"
    }),
    password: z.string({
        required_error: "密码不能为空",
    }).min(1, {
        message: "密码不能为空"
    }).min(6, {
        message: "密码至少6位"
    }).max(32, {
        message: "密码最多32位"
    }),
});

const BottomGradient = () => {
    return (
        <>
            <span className="group-hover/btn:opacity-100 block transition duration-500 opacity-0 absolute h-px w-full -bottom-px inset-x-0 bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />
            <span className="group-hover/btn:opacity-100 blur-sm block transition duration-500 opacity-0 absolute h-px w-1/2 mx-auto -bottom-px inset-x-10 bg-gradient-to-r from-transparent via-indigo-500 to-transparent" />
        </>
    );
};

const LabelInputContainer = ({
    children,
    className,
}: {
    children: React.ReactNode;
    className?: string;
}) => {
    return (
        <div className={cn("flex flex-col space-y-2 w-full", className)}>
            {children}
        </div>
    );
};


export function SignInForm({ className, user }: UserSignInFormProps) {

    const router = useRouter();
    // get query from url
    const searchParams = useSearchParams();
    const error = searchParams.get('error');
    const callbackUrl = searchParams.get('callbackUrl');

    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            email: "jsmith@example.com",
            password: "password",
        },
    });

    const onHandleSubmitAction = async (values: z.infer<typeof FormSchema>) => {
        // if (callbackUrl) {
        //     router.push(callbackUrl);
        // } else {
        //     router.push(MAIN_APP.HOME);
        // }
        // console.log("values", values);
        await signIn("credentials", {
            id: "1",
            email: values.email,
            name: "John Smith",
            token: "token",
            callbackUrl: callbackUrl ?? MAIN_APP.DASHBOARD,
        }
        )

    };
    return (
        <>
            <Form {...form}>
                {error && <p style={{ color: "red" }}>Error: {decodeURIComponent(error as string)}</p>}
                <form className={className} onSubmit={form.handleSubmit(onHandleSubmitAction)}>
                    <FormField
                        control={form.control}
                        name="email"
                        render={({ field }) => (
                            <FormItem>
                                <LabelInputContainer className="mb-4">
                                    <Label htmlFor="email">邮箱</Label>
                                    <Input id="email" placeholder="projectmayhem@fc.com" type="email" {...field} />
                                    <FormMessage />
                                </LabelInputContainer>
                            </FormItem>
                        )} />
                    <FormField
                        control={form.control}
                        name="password"
                        render={({ field }) => (
                            <FormItem>
                                <LabelInputContainer className="mb-4">
                                    <Label htmlFor="password">密码</Label>
                                    <Input id="password" placeholder="••••••••" type="password" {...field} />
                                    <FormMessage />
                                </LabelInputContainer>
                            </FormItem>
                        )} />

                    <div className="flex flex-col space-y-4">
                        <Button
                            className="bg-gradient-to-br relative group/btn from-black dark:from-zinc-900 dark:to-zinc-900 to-neutral-600 block dark:bg-zinc-800 w-full text-white rounded-md h-10 font-medium shadow-[0px_1px_0px_0px_#ffffff40_inset,0px_-1px_0px_0px_#ffffff40_inset] dark:shadow-[0px_1px_0px_0px_var(--zinc-800)_inset,0px_-1px_0px_0px_var(--zinc-800)_inset]"
                            variant="outline"
                            type="submit"
                        >
                            登录 &rarr;
                            <BottomGradient />
                        </Button>
                    </div>

                    <div className="flex flex-col space-y-4 mt-4">
                        <Button
                            variant="outline"
                            type="button"
                            onClick={() => router.push(AUTHENTICATION_APP.SignUp)}
                        >
                            注册账号 &rarr;
                            <BottomGradient />
                        </Button>
                    </div>

                    <div className="bg-gradient-to-r from-transparent via-neutral-300 dark:via-neutral-700 to-transparent my-8 h-[1px] w-full" />

                </form>
            </Form>
        </>
    )
}