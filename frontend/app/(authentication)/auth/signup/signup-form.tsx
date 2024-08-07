'use client';

import { cn } from "@/lib/utils";
import { AccountInfo } from "@/types";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { AUTHENTICATION_APP } from "@/lib/routes";

import { Form, FormField, FormItem, FormMessage } from "@/components/ui/form";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { APIResponse, buildServerURL, parserServerResponse, serverAPI } from "@/lib/api";

interface SignUpFormProps extends React.HTMLAttributes<HTMLDivElement> {
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
    }).min(6, {
        message: "密码至少6位"
    }),
    passwordConfirm: z.string({
        required_error: "密码不能为空",
    }).min(6, {
        message: "密码至少6位"
    }),
}).refine(data => data.password === data.passwordConfirm, {
    message: "两次密码输入不一致",
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


export function SignUpForm({ className }: SignUpFormProps) {
    const router = useRouter();
    // get query from url

    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            email: "jsmith@example.com",
            password: "password",
            passwordConfirm: "password",
        },
    });

    const onHandleSubmitAction = async (values: z.infer<typeof FormSchema>) => {

        try {
            const path = buildServerURL("api/auth/register");
            const resp = await serverAPI.post(path, {
                json: {
                    email: values.email,
                    password: values.password
                }
            });
            const data: APIResponse<number> = await parserServerResponse(resp);
            console.log(`data: ${JSON.stringify(data)}`);
        } catch (e) {
            console.log(`error: ${e}`);
        }
    };
    return (
        <>
            <Form {...form}>
                <form className={className} onSubmit={form.handleSubmit(onHandleSubmitAction)}>

                    <FormField
                        control={form.control}
                        name="email"
                        render={({ field }) => (
                            <FormItem>
                                <LabelInputContainer>
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
                                <LabelInputContainer className="mt-4 mb-4">
                                    <Label htmlFor="password">密码</Label>
                                    <Input id="password" placeholder="••••••••" type="password" {...field} />
                                    <FormMessage />
                                </LabelInputContainer>
                            </FormItem>
                        )} />

                    <FormField
                        control={form.control}
                        name="passwordConfirm"
                        render={({ field }) => (
                            <FormItem>
                                <LabelInputContainer className="mb-4">
                                    <Label htmlFor="passwordConfirm">确认密码</Label>
                                    <Input id="passwordConfirm" placeholder="••••••••" type="password" {...field} />
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
                            创建账号 &rarr;
                        </Button>
                    </div>

                    <div className="flex flex-col space-y-4">
                        <Button
                            variant="outline"
                            type="button"
                            onClick={() => router.push(AUTHENTICATION_APP.SignIn)}
                        >
                            &larr; 已有账号？登录
                            <BottomGradient />
                        </Button>
                    </div>
                    <div className="bg-gradient-to-r from-transparent via-neutral-300 dark:via-neutral-700 to-transparent my-8 h-[1px] w-full" />

                </form>
            </Form>
        </>
    )
}