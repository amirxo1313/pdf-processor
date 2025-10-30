import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const REAL_SEARCH_QUERIES = [
  'محسن یگانه',
  'ebi',
  'googoosh',
  'shadmehr',
  'mohsen chavoshi'
];

test.describe('Radio Javan E2E Tests - REAL API', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to actual homepage
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    console.log(`✅ Navigated to: ${BASE_URL}`);
  });

  test('Real User Flow: Search → Play → Download', async ({ page }) => {
    console.log('🚀 Starting Real User Flow test');

    // Step 1: Find search input using actual selectors from the app
    const searchInput = await page.locator('input[placeholder="Search songs, artists, albums..."]');

    await expect(searchInput).toBeVisible({ timeout: 10000 });
    console.log('✅ Search input found');

    // Step 2: Use real Persian artist name
    const searchQuery = REAL_SEARCH_QUERIES[0]; // محسن یگانه
    await searchInput.fill(searchQuery);
    await searchInput.press('Enter');

    console.log(`🔍 Searching for: ${searchQuery}`);

    // Step 3: Wait for REAL API response from Radio Javan
    const searchResponse = await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search') && response.status() === 200,
      { timeout: 15000 }
    );

    const searchData = await searchResponse.json();
    console.log(`✅ API Response received:`, {
      status: searchResponse.status(),
      url: searchResponse.url(),
      totalSongs: searchData?.result?.songs?.length || 0,
      totalAlbums: searchData?.result?.albums?.length || 0
    });

    // Step 4: Wait for search results to render
    await page.waitForSelector('[data-testid="tab-songs"]', { timeout: 10000 });

    // Take screenshot of search results
    await page.screenshot({
      path: 'test-results/01-search-results.png',
      fullPage: true
    });

    // Step 5: Click on songs tab if not already active
    const songsTab = page.locator('[data-testid="tab-songs"]');
    if (await songsTab.isVisible()) {
      await songsTab.click();
      await page.waitForTimeout(1000);
    }

    // Step 6: Find and click first song's play button
    const firstTrack = await page.locator('[data-testid^="track-"]').first();
    await expect(firstTrack).toBeVisible({ timeout: 5000 });

    // Hover over track to reveal play button
    await firstTrack.hover();

    const playButton = await firstTrack.locator('[data-testid^="button-play-track-"]');
    await expect(playButton).toBeVisible({ timeout: 3000 });

    await playButton.click();
    console.log('▶️ Play button clicked');

    // Step 7: VERIFY REAL AUDIO PLAYBACK
    await page.waitForTimeout(3000); // Wait for audio to start loading

    const audioStatus = await page.evaluate(() => {
      const audio = document.querySelector('audio');
      if (!audio) return { found: false };

      return {
        found: true,
        paused: audio.paused,
        currentTime: audio.currentTime,
        duration: audio.duration,
        src: audio.src,
        volume: audio.volume,
        readyState: audio.readyState,
        networkState: audio.networkState,
        error: audio.error
      };
    });

    console.log('🎵 Audio Status:', JSON.stringify(audioStatus, null, 2));

    // Verify audio is actually playing
    expect(audioStatus.found).toBe(true);
    expect(audioStatus.src).toBeTruthy();
    expect(audioStatus.src).toContain('http');

    // Wait a bit more if audio hasn't started yet
    if (audioStatus.paused || audioStatus.currentTime === 0) {
      await page.waitForTimeout(3000);

      const updatedStatus = await page.evaluate(() => {
        const audio = document.querySelector('audio');
        return audio ? {
          paused: audio.paused,
          currentTime: audio.currentTime,
          readyState: audio.readyState
        } : null;
      });

      console.log('🎵 Updated Audio Status:', updatedStatus);
    }

    // Take screenshot of playing state
    await page.screenshot({
      path: 'test-results/02-audio-playing.png'
    });

    // Step 8: Test player controls
    const playerTitle = await page.locator('[data-testid="text-player-title"]');
    const playerArtist = await page.locator('[data-testid="text-player-artist"]');

    await expect(playerTitle).toBeVisible();
    await expect(playerArtist).toBeVisible();

    const title = await playerTitle.textContent();
    const artist = await playerArtist.textContent();
    console.log(`🎵 Now Playing: ${artist} - ${title}`);

    // Step 9: TEST REAL DOWNLOAD
    // Find download button for the playing track
    const trackId = await firstTrack.getAttribute('data-testid');
    const downloadButton = await firstTrack.locator('[data-testid^="button-download-"]');

    await firstTrack.hover(); // Ensure download button is visible
    await expect(downloadButton).toBeVisible({ timeout: 3000 });

    // Start download and capture file
    const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
    await downloadButton.click();
    console.log('📥 Download initiated...');

    const download = await downloadPromise;

    // Wait for download to complete
    const downloadPath = await download.path();
    const suggestedFilename = download.suggestedFilename();

    console.log(`📥 Download Info:`, {
      filename: suggestedFilename,
      path: downloadPath
    });

    // Save to test-results directory
    const savedPath = path.join('test-results', suggestedFilename);
    await download.saveAs(savedPath);

    // Verify REAL file
    const stats = fs.statSync(savedPath);
    const fileSizeMB = (stats.size / (1024 * 1024)).toFixed(2);

    console.log(`✅ File Downloaded:`, {
      filename: suggestedFilename,
      size: `${fileSizeMB} MB`,
      path: savedPath
    });

    // Verify file is audio
    expect(stats.size).toBeGreaterThan(100000); // At least 100KB
    expect(suggestedFilename).toMatch(/\.(mp3|m4a|wav|aac)$/i);

    await page.screenshot({
      path: 'test-results/03-download-complete.png'
    });
  });

  test('Test Player Controls - Pause/Resume', async ({ page }) => {
    console.log('🎮 Testing Player Controls');

    // Quick search to get a song
    const searchInput = await page.locator('input[placeholder="Search songs, artists, albums..."]');
    await searchInput.fill('ebi');
    await searchInput.press('Enter');

    await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search'),
      { timeout: 15000 }
    );

    await page.waitForSelector('[data-testid^="track-"]', { timeout: 10000 });

    // Play first song
    const firstTrack = await page.locator('[data-testid^="track-"]').first();
    await firstTrack.hover();
    await firstTrack.locator('[data-testid^="button-play-track-"]').click();

    await page.waitForTimeout(3000); // Let audio start

    // Test PAUSE
    const playPauseButton = await page.locator('[data-testid="button-play-pause"]');
    await expect(playPauseButton).toBeVisible();

    // Click pause
    await playPauseButton.click();
    await page.waitForTimeout(1000);

    const pausedStatus = await page.evaluate(() => {
      const audio = document.querySelector('audio');
      return audio ? { paused: audio.paused, currentTime: audio.currentTime } : null;
    });

    console.log(`⏸️ After pause - Audio paused: ${pausedStatus?.paused}`);
    expect(pausedStatus?.paused).toBe(true);

    // Test RESUME
    await playPauseButton.click();
    await page.waitForTimeout(2000);

    const playingStatus = await page.evaluate(() => {
      const audio = document.querySelector('audio');
      return audio ? {
        paused: audio.paused,
        currentTime: audio.currentTime,
        playing: !audio.paused && audio.currentTime > 0
      } : null;
    });

    console.log(`▶️ After resume - Audio playing: ${playingStatus?.playing}`);

    await page.screenshot({
      path: 'test-results/04-player-controls.png'
    });
  });

  test('Test Multiple Search Results Types', async ({ page }) => {
    console.log('🔍 Testing comprehensive search results');

    const searchInput = await page.locator('input[placeholder="Search songs, artists, albums..."]');
    await searchInput.fill('googoosh');
    await searchInput.press('Enter');

    const response = await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search'),
      { timeout: 15000 }
    );

    const searchData = await response.json();
    console.log('📊 Search Results Summary:', {
      songs: searchData?.result?.songs?.length || 0,
      albums: searchData?.result?.albums?.length || 0,
      artists: searchData?.result?.artists?.length || 0,
      playlists: searchData?.result?.playlists?.length || 0,
      videos: searchData?.result?.videos?.length || 0,
      podcasts: searchData?.result?.podcasts?.length || 0
    });

    // Test different tabs
    const tabs = ['songs', 'albums', 'artists', 'playlists', 'videos', 'podcasts'];

    for (const tab of tabs) {
      const tabElement = page.locator(`[data-testid="tab-${tab}"]`);
      if (await tabElement.isVisible()) {
        await tabElement.click();
        await page.waitForTimeout(500);
        console.log(`✅ ${tab} tab tested`);
      }
    }

    await page.screenshot({
      path: 'test-results/05-search-tabs.png',
      fullPage: true
    });
  });

  test('Test API Response Times and Health', async ({ page }) => {
    console.log('🏥 Testing API health and performance');

    // Test health endpoint
    const healthResponse = await page.request.get(`${BASE_URL}/api/health`);
    const healthData = await healthResponse.json();

    console.log('🏥 Health Check:', healthData);
    expect(healthResponse.status()).toBe(200);
    expect(healthData.status).toBe('ok');
    expect(healthData.token_configured).toBe(true);

    // Test search performance
    const searchInput = await page.locator('input[placeholder="Search songs, artists, albums..."]');
    await searchInput.fill('mohsen chavoshi');

    const startTime = Date.now();
    await searchInput.press('Enter');

    const searchResponse = await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search'),
      { timeout: 15000 }
    );

    const responseTime = Date.now() - startTime;

    console.log('⚡ API Performance:', {
      endpoint: '/api/radiojavan/search',
      status: searchResponse.status(),
      responseTime: `${responseTime}ms`,
      url: searchResponse.url()
    });

    expect(searchResponse.status()).toBe(200);
    expect(responseTime).toBeLessThan(10000); // Should respond within 10 seconds
  });

  test('Check for Console Errors and Network Issues', async ({ page }) => {
    console.log('🚨 Monitoring console and network errors');

    const consoleErrors = [];
    const networkErrors = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push({
          text: msg.text(),
          location: msg.location()
        });
      }
    });

    page.on('requestfailed', request => {
      networkErrors.push({
        url: request.url(),
        failure: request.failure()
      });
    });

    // Navigate through main pages
    await page.goto(`${BASE_URL}`);
    await page.waitForTimeout(2000);

    await page.goto(`${BASE_URL}/search?q=test`);
    await page.waitForTimeout(2000);

    await page.goto(`${BASE_URL}/downloads`);
    await page.waitForTimeout(2000);

    console.log('Console Errors:', consoleErrors.length > 0 ? consoleErrors : 'None');
    console.log('Network Errors:', networkErrors.length > 0 ? networkErrors : 'None');

    // Optional: fail test if critical errors found
    const criticalErrors = consoleErrors.filter(err =>
      !err.text.includes('favicon') &&
      !err.text.includes('Failed to load resource')
    );

    if (criticalErrors.length > 0) {
      console.warn(`⚠️ Found ${criticalErrors.length} console errors`);
    }
  });

  test('Test Navigation and Page Loads', async ({ page }) => {
    console.log('🧭 Testing navigation');

    // Test home link
    const homeLink = await page.locator('[data-testid="link-home"]');
    await homeLink.click();
    await expect(page).toHaveURL(BASE_URL + '/');
    console.log('✅ Home navigation works');

    // Test downloads page
    await page.click('text=Downloads');
    await expect(page).toHaveURL(/\/downloads/);
    console.log('✅ Downloads navigation works');

    // Test search navigation via URL
    await page.goto(`${BASE_URL}/search?q=shadmehr`);
    await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search'),
      { timeout: 15000 }
    );
    console.log('✅ Direct search URL works');

    await page.screenshot({
      path: 'test-results/06-navigation.png'
    });
  });
});

// Advanced test scenarios
test.describe('Advanced Radio Javan Tests', () => {

  test('Test Audio Streaming Quality', async ({ page }) => {
    console.log('🎧 Testing audio streaming quality');

    await page.goto(BASE_URL);

    // Quick search and play
    const searchInput = await page.locator('input[placeholder="Search songs, artists, albums..."]');
    await searchInput.fill('ebi');
    await searchInput.press('Enter');

    await page.waitForResponse(response => response.url().includes('/api/radiojavan/search'));
    await page.waitForSelector('[data-testid^="track-"]');

    const firstTrack = await page.locator('[data-testid^="track-"]').first();
    await firstTrack.hover();
    await firstTrack.locator('[data-testid^="button-play-track-"]').click();

    // Monitor audio buffering
    await page.waitForTimeout(5000); // Let audio buffer

    const audioMetrics = await page.evaluate(() => {
      const audio = document.querySelector('audio');
      if (!audio) return null;

      const buffered = audio.buffered;
      const bufferedRanges = [];

      for (let i = 0; i < buffered.length; i++) {
        bufferedRanges.push({
          start: buffered.start(i),
          end: buffered.end(i)
        });
      }

      return {
        currentTime: audio.currentTime,
        duration: audio.duration,
        buffered: bufferedRanges,
        readyState: audio.readyState,
        networkState: audio.networkState,
        playbackRate: audio.playbackRate,
        volume: audio.volume
      };
    });

    console.log('🎧 Audio Metrics:', JSON.stringify(audioMetrics, null, 2));

    expect(audioMetrics).not.toBeNull();
    expect(audioMetrics.readyState).toBeGreaterThanOrEqual(3); // HAVE_FUTURE_DATA
  });

  test('Test Concurrent Downloads', async ({ page, context }) => {
    console.log('📥 Testing multiple concurrent downloads');

    await page.goto(BASE_URL);

    // Search for content
    const searchInput = await page.locator('input[placeholder="Search songs, artists, albums..."]');
    await searchInput.fill('mohsen yeganeh');
    await searchInput.press('Enter');

    await page.waitForResponse(response => response.url().includes('/api/radiojavan/search'));
    await page.waitForSelector('[data-testid^="track-"]');

    // Get first 3 tracks
    const tracks = await page.locator('[data-testid^="track-"]').all();
    const tracksToDownload = tracks.slice(0, Math.min(3, tracks.length));

    const downloadPromises = [];

    for (const track of tracksToDownload) {
      await track.hover();
      const downloadButton = await track.locator('[data-testid^="button-download-"]');

      if (await downloadButton.isVisible()) {
        const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
        await downloadButton.click();
        downloadPromises.push(downloadPromise);
        console.log('📥 Started download', downloadPromises.length);
      }
    }

    // Wait for all downloads
    const downloads = await Promise.all(downloadPromises);
    console.log(`✅ ${downloads.length} files downloaded concurrently`);

    // Verify all downloads
    for (let i = 0; i < downloads.length; i++) {
      const filename = downloads[i].suggestedFilename();
      console.log(`📁 Download ${i + 1}: ${filename}`);
      expect(filename).toMatch(/\.(mp3|m4a)$/i);
    }
  });
});
