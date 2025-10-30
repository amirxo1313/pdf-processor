import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 1,
  workers: 1,
  timeout: 60000,

  expect: {
    timeout: 10000
  },

  reporter: [
    ['html', { outputFolder: 'test-results/html-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list']
  ],

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    screenshot: 'on',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
    viewport: { width: 1920, height: 1080 },
    acceptDownloads: true,
    launchOptions: {
      args: [
        '--autoplay-policy=no-user-gesture-required',
        '--use-fake-ui-for-media-stream'
      ]
    }
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    }
  ],
});
