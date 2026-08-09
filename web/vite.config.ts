import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    VitePWA({
      // Auto-update: the new service worker takes over as soon as it is
      // installed; the page reloads in the background so users always run
      // the latest build without manual intervention.
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'MARS Constech REM ERP',
        short_name: 'REM ERP',
        description: 'Production ERP for MARS Constech — bookings, CRM, dues, projects and more.',
        theme_color: '#2f80ed',
        background_color: '#0d1b2a',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        scope: '/',
        lang: 'en',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ]
      },
      workbox: {
        // API data sync + static assets:
        // - Static assets (JS/CSS/images): StaleWhileRevalidate — instant
        //   shell from cache, refreshed in the background.
        // - Same-origin API calls (the Frappe bridge): NetworkFirst — always
        //   try the network first so server data stays fresh, fall back to
        //   the cache only when offline.
        globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2}'],
        navigateFallback: '/index.html',
        runtimeCaching: [
          {
            // API endpoints (mars_constech bridge) — NetworkFirst
            urlPattern: ({ url }) =>
              url.pathname.startsWith('/api/method/mars_constech') ||
              url.pathname.includes('/api/method/mars_constech'),
            handler: 'NetworkFirst',
            method: 'GET',
            options: {
              cacheName: 'rem-erp-api',
              networkTimeoutSeconds: 8,
              expiration: {
                maxEntries: 64,
                maxAgeSeconds: 60 * 60 // 1 hour
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          {
            // Static assets — StaleWhileRevalidate
            urlPattern: ({ request }) =>
              request.destination === 'script' ||
              request.destination === 'style' ||
              request.destination === 'image' ||
              request.destination === 'font',
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'rem-erp-static',
              expiration: {
                maxEntries: 128,
                maxAgeSeconds: 30 * 24 * 60 * 60 // 30 days
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      },
      devOptions: {
        enabled: true
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
