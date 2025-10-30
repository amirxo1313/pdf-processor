import { test, expect, devices } from '@playwright/test';
import {
  searchAndWaitForResults,
  playTrackByIndex,
  waitForAudioPlaying,
  getPlayerState
} from './helpers/test-utils.js';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

// Test on mobile devices
test.describe('Radio Javan Mobile E2E Tests', () => {

  test.use({
    ...devices['iPhone 13']
  });

  test('Mobile: Search and Play on iPhone', async ({ page }) => {
    console.log('📱 Testing on iPhone 13');

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Check mobile responsive design
    const viewport = page.viewportSize();
    console.log(`📱 Viewport: ${viewport.width}x${viewport.height}`);

    // Search functionality on mobile
    const searchData = await searchAndWaitForResults(page, 'گوگوش');
    console.log('🔍 Mobile search results:', {
      songs: searchData?.result?.songs?.length || 0
    });

    // Play a song on mobile
    await playTrackByIndex(page, 0);

    // Verify audio playback on mobile
    const audioStatus = await waitForAudioPlaying(page);
    expect(audioStatus.playing).toBe(true);

    // Take mobile screenshot
    await page.screenshot({
      path: 'test-results/mobile-iphone-playing.png',
      fullPage: true
    });
  });

  test.describe('Android Tests', () => {
    test.use({
      ...devices['Pixel 5']
    });

    test('Mobile: Android Download Test', async ({ page }) => {
      console.log('📱 Testing on Android Pixel 5');

      await page.goto(BASE_URL);

      // Test search on Android
      const searchData = await searchAndWaitForResults(page, 'mohsen yeganeh');

      // Verify mobile UI elements
      const searchInput = page.locator('input[placeholder*="Search"]');
      await expect(searchInput).toBeVisible();

      // Play first result
      const firstTrack = await page.locator('[data-testid^="track-"]').first();
      await firstTrack.tap(); // Use tap for mobile

      const playButton = await firstTrack.locator('[data-testid^="button-play-track-"]');
      await playButton.tap();

      await page.waitForTimeout(2000);

      // Test download on mobile
      const downloadButton = await firstTrack.locator('[data-testid^="button-download-"]');

      if (await downloadButton.isVisible()) {
        const downloadPromise = page.waitForEvent('download');
        await downloadButton.tap();

        const download = await downloadPromise;
        console.log(`📥 Mobile download: ${download.suggestedFilename()}`);
      }

      await page.screenshot({
        path: 'test-results/mobile-android-playing.png'
      });
    });
  });

  test('Mobile: Gesture Navigation', async ({ page }) => {
    test.use({
      ...devices['iPhone 12 Pro']
    });

    await page.goto(BASE_URL);

    // Test swipe gestures if implemented
    const searchResults = await searchAndWaitForResults(page, 'ebi');

    // Simulate swipe between tabs
    const tabsContainer = page.locator('[role="tablist"]');
    if (await tabsContainer.isVisible()) {
      await tabsContainer.swipe({
        direction: 'left',
        distance: 100
      });

      await page.waitForTimeout(500);
    }

    // Test touch interactions
    const tracks = await page.locator('[data-testid^="track-"]').all();
    if (tracks.length > 0) {
      // Long press to show options (if implemented)
      await tracks[0].tap({ delay: 1000 });
    }
  });
});

// Cross-browser testing
test.describe('Cross-Browser Compatibility', () => {

  const browsers = [
    { name: 'Chrome', project: 'chromium' },
    { name: 'Firefox', project: 'firefox' },
    { name: 'Safari', project: 'webkit' }
  ];

  for (const browser of browsers) {
    test(`${browser.name}: Basic Functionality`, async ({ page, browserName }) => {
      if (browserName !== browser.project) {
        test.skip();
        return;
      }

      console.log(`🌐 Testing on ${browser.name}`);

      await page.goto(BASE_URL);

      // Test search across browsers
      const searchData = await searchAndWaitForResults(page, 'shadmehr');
      expect(searchData?.result?.songs?.length).toBeGreaterThan(0);

      // Test audio playback compatibility
      await playTrackByIndex(page, 0);

      // Browser-specific audio checks
      const audioSupport = await page.evaluate(() => {
        const audio = document.createElement('audio');
        return {
          mp3: audio.canPlayType('audio/mpeg'),
          m4a: audio.canPlayType('audio/mp4'),
          ogg: audio.canPlayType('audio/ogg'),
          webm: audio.canPlayType('audio/webm')
        };
      });

      console.log(`🎵 ${browser.name} audio support:`, audioSupport);

      await page.screenshot({
        path: `test-results/browser-${browser.project}.png`
      });
    });
  }
});

// Performance testing
test.describe('Performance Tests', () => {

  test('Page Load Performance', async ({ page }) => {
    console.log('⚡ Testing page load performance');

    const metrics = [];

    // Test multiple page loads
    for (let i = 0; i < 3; i++) {
      const startTime = Date.now();

      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      const loadTime = Date.now() - startTime;

      const performanceMetrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0];
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
          firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
        };
      });

      metrics.push({
        iteration: i + 1,
        loadTime,
        ...performanceMetrics
      });
    }

    console.log('⚡ Performance Metrics:', metrics);

    // Calculate averages
    const avgLoadTime = metrics.reduce((sum, m) => sum + m.loadTime, 0) / metrics.length;
    console.log(`⚡ Average page load time: ${avgLoadTime}ms`);

    // Performance assertions
    expect(avgLoadTime).toBeLessThan(5000); // Page should load within 5 seconds
  });

  test('Search Performance Under Load', async ({ page }) => {
    console.log('🔍 Testing search performance');

    await page.goto(BASE_URL);

    const searchQueries = ['ebi', 'googoosh', 'mohsen', 'shadmehr', 'benyamin'];
    const searchTimes = [];

    for (const query of searchQueries) {
      const searchInput = await page.locator('input[placeholder*="Search"]');
      await searchInput.clear();

      const startTime = Date.now();
      await searchInput.fill(query);
      await searchInput.press('Enter');

      await page.waitForResponse(
        response => response.url().includes('/api/radiojavan/search'),
        { timeout: 15000 }
      );

      const searchTime = Date.now() - startTime;
      searchTimes.push({ query, time: searchTime });

      await page.waitForTimeout(1000); // Avoid rate limiting
    }

    console.log('🔍 Search Performance Results:', searchTimes);

    const avgSearchTime = searchTimes.reduce((sum, s) => sum + s.time, 0) / searchTimes.length;
    console.log(`🔍 Average search time: ${avgSearchTime}ms`);

    expect(avgSearchTime).toBeLessThan(3000);
  });
});

// Accessibility testing
test.describe('Accessibility Tests', () => {

  test('Keyboard Navigation', async ({ page }) => {
    console.log('⌨️ Testing keyboard navigation');

    await page.goto(BASE_URL);

    // Tab through interactive elements
    await page.keyboard.press('Tab');
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName);
    console.log('First focused element:', firstFocused);

    // Navigate to search
    const searchInput = await page.locator('input[placeholder*="Search"]');
    await searchInput.focus();
    await searchInput.fill('ebi');
    await page.keyboard.press('Enter');

    await page.waitForResponse(response => response.url().includes('/api/radiojavan/search'));

    // Tab to first result
    await page.waitForSelector('[data-testid^="track-"]');

    // Use keyboard to play
    let tabCount = 0;
    while (tabCount < 20) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => {
        const el = document.activeElement;
        return {
          tag: el?.tagName,
          testId: el?.getAttribute('data-testid'),
          ariaLabel: el?.getAttribute('aria-label')
        };
      });

      if (focused.testId?.includes('button-play-track')) {
        await page.keyboard.press('Enter');
        console.log('✅ Played track using keyboard');
        break;
      }

      tabCount++;
    }

    await page.waitForTimeout(2000);

    // Test player keyboard controls
    const playerButton = await page.locator('[data-testid="button-play-pause"]');
    await playerButton.focus();
    await page.keyboard.press('Space'); // Pause

    await page.waitForTimeout(1000);

    const isPaused = await page.evaluate(() => {
      const audio = document.querySelector('audio');
      return audio?.paused;
    });

    expect(isPaused).toBe(true);
    console.log('✅ Keyboard controls work');
  });

  test('Screen Reader Compatibility', async ({ page }) => {
    console.log('🔊 Testing screen reader compatibility');

    await page.goto(BASE_URL);

    // Check ARIA labels
    const ariaElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('[aria-label], [role]');
      return Array.from(elements).map(el => ({
        tag: el.tagName,
        role: el.getAttribute('role'),
        ariaLabel: el.getAttribute('aria-label'),
        ariaDescribedBy: el.getAttribute('aria-describedby')
      }));
    });

    console.log(`Found ${ariaElements.length} accessible elements`);

    // Check main landmarks
    const landmarks = await page.evaluate(() => {
      const main = document.querySelector('main');
      const nav = document.querySelector('nav');
      const header = document.querySelector('header');

      return {
        hasMain: !!main,
        hasNav: !!nav,
        hasHeader: !!header
      };
    });

    expect(landmarks.hasMain).toBe(true);
    console.log('✅ Page has proper landmarks:', landmarks);
  });
});
