import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

const host = process.env.TAURI_DEV_HOST;

// https://vitejs.dev/config/
export default defineConfig(() => {
  const isDesktopBuild = process.env.BUILD_TARGET === "desktop";

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },

    // 构建配置
    build: isDesktopBuild
      ? {
          // 桌面应用构建配置
          outDir: "../desktop/static",
          emptyOutDir: true,
          rollupOptions: {
            output: {
              manualChunks: undefined, // 减少文件分片，简化部署
            },
          },
          // 生成源映射用于调试
          sourcemap: false,
          // 针对桌面环境优化
          target: "esnext",
          minify: "esbuild" as const,
        }
      : {
          // 默认Web构建配置
          outDir: "dist",
          emptyOutDir: true,
        },

    // 基础路径配置
    base: isDesktopBuild ? "./" : "/",

    // 开发服务器配置（保持原有的Tauri配置）
    clearScreen: false,
    server: {
      port: 1420,
      strictPort: true,
      host: host || false,
      hmr: host
        ? {
            protocol: "ws",
            host: host,
            port: 1421,
          }
        : undefined,
      watch: {
        ignored: ["**/src-tauri/**"],
      },
    },
  };
});
