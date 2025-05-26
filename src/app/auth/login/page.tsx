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
import { User, Lock, AlertCircle, Building } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

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
        <Card className="w-full">
            <CardHeader className="space-y-1">
                <div className="flex items-center justify-center space-x-2">
                    <Building className="h-6 w-6 text-primary" />
                    <CardTitle className="text-2xl">欢迎回来</CardTitle>
                </div>
                <CardDescription className="text-center">
                    请输入您的账号信息登录系统
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="username" className="text-sm font-medium">
                            用户名
                        </Label>
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                id="username"
                                placeholder="请输入用户名"
                                className={`pl-10 ${errors.username ? "border-destructive ring-destructive" : ""}`}
                                {...register("username")}
                            />
                        </div>
                        {errors.username && (
                            <div className="flex items-center text-destructive text-sm">
                                <AlertCircle className="h-3.5 w-3.5 mr-1" />
                                <span>{errors.username.message}</span>
                            </div>
                        )}
                    </div>

                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <Label htmlFor="password" className="text-sm font-medium">
                                密码
                            </Label>
                            <a
                                href="#"
                                className="text-xs text-primary hover:underline"
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
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                id="password"
                                type="password"
                                placeholder="请输入密码"
                                className={`pl-10 ${errors.password ? "border-destructive ring-destructive" : ""}`}
                                {...register("password")}
                            />
                        </div>
                        {errors.password && (
                            <div className="flex items-center text-destructive text-sm">
                                <AlertCircle className="h-3.5 w-3.5 mr-1" />
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
                        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-md flex items-center text-sm">
                            <AlertCircle className="h-4 w-4 mr-2" />
                            {error}
                        </div>
                    )}

                    <Button
                        type="submit"
                        className="w-full"
                        size="lg"
                        disabled={loading}
                    >
                        {loading ? <LoadingSpinner className="mr-2 h-4 w-4" /> : null}
                        {loading ? "登录中..." : "登 录"}
                    </Button>
                </form>
            </CardContent>
            <CardFooter className="flex justify-center">
                <p className="text-xs text-muted-foreground px-4 text-center">
                    登录即表示您同意我们的服务条款和隐私政策
                </p>
            </CardFooter>
        </Card>
    );
}