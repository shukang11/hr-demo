import Link from "next/link";
import Image from "next/image";
import { PanelsTopLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { Icons } from "@/components/icons";
import { siteConfig } from "@/lib/constant";
import { AUTHENTICATION_APP, MAIN_APP } from "@/lib/routes";
import { getCurrentUser } from "@/lib/session";

export default async function HomePage() {
    const user = (await getCurrentUser()) || null;


    return (
        <div className="flex flex-col min-h-screen">
            <header className="z-[50] sticky top-0 w-full bg-background/95 border-b backdrop-blur-sm dark:bg-black/[0.6] border-border/40">
                <div className="container h-14 flex items-center">
                    <Link
                        href="/"
                        className="flex justify-start items-center hover:opacity-85 transition-opacity duration-300"
                    >
                        <PanelsTopLeft className="w-6 h-6 mr-3" />
                        <span className="font-bold">{siteConfig.title}</span>
                        <span className="sr-only">{siteConfig.title}</span>
                    </Link>
                    <nav className="ml-auto flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="icon"
                            className="rounded-full w-8 h-8 bg-background"
                            asChild
                        >
                            <Link href="https://github.com/salimi-my/shadcn-ui-sidebar">
                                <Icons.gitHub className="h-[1.2rem] w-[1.2rem]" />
                            </Link>
                        </Button>
                        <ThemeToggle />
                    </nav>
                </div>
            </header>
            <main className="min-h-[calc(100vh-57px-97px)] flex-1">
                <div className="container relative pb-10">
                    <section className="mx-auto flex max-w-[980px] flex-col items-center gap-2 py-8 md:py-12 md:pb-8 lg:py-24 lg:pb-6">
                        <h1 className="text-center text-3xl font-bold leading-tight tracking-tighter md:text-5xl lg:leading-[1.1]">
                            {siteConfig.title}
                        </h1>
                        <span className="max-w-[750px] text-center text-lg font-light text-foreground">
                            {siteConfig.description}
                        </span>
                        <div className="flex w-full items-center justify-center space-x-4 py-4 md:pb-6">
                            <Button variant="default" asChild>
                                <Link href={user ? MAIN_APP.DASHBOARD : AUTHENTICATION_APP.SignIn}>
                                    {user ? "开始使用" : "登录"}
                                    <Icons.arrowRight className="ml-2" />
                                </Link>
                            </Button>
                            <Button variant="outline" asChild>
                                <Link
                                    href="https://ui.shadcn.com/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    Learn shadcn/ui
                                </Link>
                            </Button>
                        </div>
                    </section>
                    <div className="w-full flex justify-center relative">

                    </div>
                </div>
            </main>
            <footer className="py-6 md:py-0 border-t border-border/40">
                <div className="container flex flex-col items-center justify-center gap-4 md:h-24 md:flex-row">
                    <p className="text-balance text-center text-sm leading-loose text-muted-foreground">
                        Built on top of{" "}
                        <Link
                            href="https://ui.shadcn.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-medium underline underline-offset-4"
                        >
                            {siteConfig.title}
                        </Link>
                        . The source code is available on{" "}
                        <Link
                            href={siteConfig.author.github}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-medium underline underline-offset-4"
                        >
                            GitHub
                        </Link>
                        .
                    </p>
                </div>
            </footer>
        </div>
    );
}