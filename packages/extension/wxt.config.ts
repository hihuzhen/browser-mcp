import {defineConfig} from 'wxt';
import {viteStaticCopy} from 'vite-plugin-static-copy';
import {config} from 'dotenv';
import {resolve} from 'path';

config({path: resolve(process.cwd(), '.env')});
config({path: resolve(process.cwd(), '.env.local')});

const CHROME_EXTENSION_KEY = process.env.CHROME_EXTENSION_KEY;

// See https://wxt.dev/api/config.html
export default defineConfig({
    modules: ['@wxt-dev/module-vue'],

    manifest: {
        key: CHROME_EXTENSION_KEY,
        default_locale: 'zh_CN',
        name: 'browser mcp',
        description: '__MSG_extensionDescription__',
        permissions: [
            'nativeMessaging',
            'tabs',
            'activeTab',
            'scripting',
            'downloads',
            'webRequest',
            'debugger',
            'history',
            'bookmarks',
            'offscreen',
            'storage'
        ],
        host_permissions: ['<all_urls>'],
        cross_origin_embedder_policy: {
            value: 'require-corp',
        },
        cross_origin_opener_policy: {
            value: 'same-origin',
        },
        content_security_policy: {
            extension_pages: "script-src 'self' 'wasm-unsafe-eval'; object-src 'self';",
        },
    },
    vite: (env) => ({
        plugins: [
            viteStaticCopy({
                targets: [
                    {
                        src: 'inject-scripts/*.js',
                        dest: 'inject-scripts',
                    },
                    {
                        src: '_locales/**/*',
                        dest: '_locales',
                    },
                ],
            }) as any,
        ],
        build: {
            // 我们的构建产物需要兼容到es6
            target: 'es2015',
            // 非生产环境下生成sourcemap
            sourcemap: env.mode !== 'production',
            // 禁用gzip 压缩大小报告，因为压缩大型文件可能会很慢
            reportCompressedSize: false,
            // chunk大小超过1500kb是触发警告
            chunkSizeWarningLimit: 1500,
            minify: false,
        }
    })
});