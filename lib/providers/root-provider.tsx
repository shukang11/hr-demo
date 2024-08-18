'use client';
import React from 'react';
import { ThemeProvider } from './theme-provider';
import { SettingProvider } from './setting-provider';

export function RootProviders({
    children
}: {
    children: React.ReactNode;
}) {
    return (
        <>
            <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
                <SettingProvider>
                    {children}
                </SettingProvider>
            </ThemeProvider>
        </>
    );
}