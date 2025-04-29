import { useState } from "react";
import { useAuth } from "@/lib/auth/auth-context";
import { useNavigate, useLocation } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useToast } from "@/hooks/use-toast";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { User, Lock, AlertCircle } from "lucide-react";

const loginFormSchema = z.object({
    username: z.string().min(1, "用户名不能为空"),
    password: z.string().min(6, "密码至少需要 6 个字符"),
    remember: z.boolean().optional(),
});

type LoginFormValues = z.infer<typeof loginFormSchema>;

export default function LoginPage() {
    const { login, loading, error } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const { toast } = useToast();

    const {
        register,
        handleSubmit,
        formState: { errors },
        setValue,
        watch,
    } = useForm<LoginFormValues>({
        resolver: zodResolver(loginFormSchema),
        defaultValues: {
            username: "",
            password: "",
            remember: false,
        },
    });

    const rememberMe = watch("remember");

    const onSubmit = async (data: LoginFormValues) => {
        try {
            await login(data.username, data.password, data.remember);
            // 如果有保存的重定向地址，登录后跳转回去
            const from = (location.state as any)?.from?.pathname || "/dashboard";
            navigate(from, { replace: true });
        } catch (err) {
            console.error("登录失败", err);
        }
    };

    return (
        <div className="space-y-6">

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                <div className="space-y-1">
                    <Label htmlFor="username" className="text-sm font-medium">
                        用户名
                    </Label>
                    <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 h-[18px] w-[18px] text-gray-500" />
                        <Input
                            id="username"
                            placeholder="请输入用户名"
                            className={`pl-10 ${errors.username ? "border-red-500 focus-visible:ring-red-500" : ""}`}
                            {...register("username")}
                        />
                    </div>
                    {errors.username && (
                        <div className="flex items-center mt-1 text-red-600 text-sm">
                            <AlertCircle className="h-4 w-4 mr-1" />
                            <span>{errors.username.message}</span>
                        </div>
                    )}
                </div>

                <div className="space-y-1">
                    <div className="flex items-center justify-between">
                        <Label htmlFor="password" className="text-sm font-medium">
                            密码
                        </Label>
                        <a
                            href="#"
                            className="text-sm text-blue-600 hover:text-blue-800 hover:underline"
                            onClick={(e) => {
                                e.preventDefault();
                                toast({
                                    title: "重置密码功能",
                                    description: "该功能尚未实现，请联系管理员",
                                });
                            }}
                        >
                            忘记密码?
                        </a>
                    </div>
                    <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-[18px] w-[18px] text-gray-500" />
                        <Input
                            id="password"
                            type="password"
                            placeholder="请输入密码"
                            className={`pl-10 ${errors.password ? "border-red-500 focus-visible:ring-red-500" : ""}`}
                            {...register("password")}
                        />
                    </div>
                    {errors.password && (
                        <div className="flex items-center mt-1 text-red-600 text-sm">
                            <AlertCircle className="h-4 w-4 mr-1" />
                            <span>{errors.password.message}</span>
                        </div>
                    )}
                </div>

                <div className="flex items-center space-x-2">
                    <Checkbox
                        id="remember"
                        checked={rememberMe}
                        onCheckedChange={(checked) => {
                            setValue("remember", checked === true);
                        }}
                    />
                    <Label
                        htmlFor="remember"
                        className="text-sm font-medium leading-none cursor-pointer"
                    >
                        记住我
                    </Label>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-center text-sm">
                        <AlertCircle className="h-4 w-4 mr-2" />
                        {error}
                    </div>
                )}

                <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white py-2 rounded-md transition-all duration-200"
                    disabled={loading}
                >
                    {loading ? <LoadingSpinner className="mr-2 h-4 w-4 text-white" /> : null}
                    {loading ? "登录中..." : "登 录"}
                </Button>
            </form>

        </div>
    );
}