'use client';
import React from 'react';
import { ThemeProvider } from './theme-provider';
import { SessionProvider } from 'next-auth/react';
import { SettingProvider } from './setting-provider';

export function RootProviders({
    children
}: {
    children: React.ReactNode;
}) {
    return (
        <>
            <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
                <SessionProvider>
                    <SettingProvider>
                    {children}
                    </SettingProvider>
                </SessionProvider>
            </ThemeProvider>
        </>
    );
}