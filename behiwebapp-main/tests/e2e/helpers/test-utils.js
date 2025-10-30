// Test utilities and helper functions
import { expect } from '@playwright/test';

/**
 * Wait for audio element to be ready and playing
 * @param {Page} page - Playwright page object
 * @param {number} timeout - Maximum wait time in milliseconds
 * @returns {Promise<Object>} Audio element status
 */
export async function waitForAudioPlaying(page, timeout = 10000) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const audioStatus = await page.evaluate(() => {
      const audio = document.querySelector('audio');
      if (!audio) return null;

      return {
        found: true,
        paused: audio.paused,
        currentTime: audio.currentTime,
        duration: audio.duration,
        src: audio.src,
        readyState: audio.readyState,
        networkState: audio.networkState,
        playing: !audio.paused && audio.currentTime > 0
      };
    });

    if (audioStatus?.playing) {
      return audioStatus;
    }

    await page.waitForTimeout(500);
  }

  throw new Error(`Audio did not start playing within ${timeout}ms`);
}

/**
 * Search for content and wait for results
 * @param {Page} page - Playwright page object
 * @param {string} query - Search query
 * @returns {Promise<Object>} Search response data
 */
export async function searchAndWaitForResults(page, query) {
  const searchInput = await page.locator('input[placeholder="Search songs, artists, albums..."]');
  await expect(searchInput).toBeVisible();

  await searchInput.fill(query);
  await searchInput.press('Enter');

  const response = await page.waitForResponse(
    response => response.url().includes('/api/radiojavan/search') && response.status() === 200,
    { timeout: 15000 }
  );

  const data = await response.json();

  // Wait for UI to update
  await page.waitForSelector('[data-testid^="tab-"]', { timeout: 10000 });

  return data;
}

/**
 * Play a track by index
 * @param {Page} page - Playwright page object
 * @param {number} index - Track index (0-based)
 */
export async function playTrackByIndex(page, index = 0) {
  const tracks = await page.locator('[data-testid^="track-"]').all();
  if (tracks.length <= index) {
    throw new Error(`No track found at index ${index}`);
  }

  const track = tracks[index];
  await track.hover();

  const playButton = await track.locator('[data-testid^="button-play-track-"]');
  await expect(playButton).toBeVisible();
  await playButton.click();

  // Wait for player to update
  await page.waitForTimeout(1000);
}

/**
 * Download a track and verify the file
 * @param {Page} page - Playwright page object
 * @param {Locator} track - Track element locator
 * @returns {Promise<Object>} Download information
 */
export async function downloadTrack(page, track) {
  await track.hover();
  const downloadButton = await track.locator('[data-testid^="button-download-"]');
  await expect(downloadButton).toBeVisible();

  const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
  await downloadButton.click();

  const download = await downloadPromise;
  const filename = download.suggestedFilename();
  const path = await download.path();

  return {
    filename,
    path,
    download
  };
}

/**
 * Get current player state
 * @param {Page} page - Playwright page object
 * @returns {Promise<Object>} Player state information
 */
export async function getPlayerState(page) {
  const title = await page.locator('[data-testid="text-player-title"]').textContent();
  const artist = await page.locator('[data-testid="text-player-artist"]').textContent();

  const audioState = await page.evaluate(() => {
    const audio = document.querySelector('audio');
    const video = document.querySelector('video');
    const media = audio || video;

    if (!media) return null;

    return {
      type: audio ? 'audio' : 'video',
      paused: media.paused,
      currentTime: media.currentTime,
      duration: media.duration,
      volume: media.volume,
      muted: media.muted,
      src: media.src
    };
  });

  return {
    title,
    artist,
    media: audioState
  };
}

/**
 * Monitor network requests during a test
 * @param {Page} page - Playwright page object
 * @param {Function} testFunction - Async function to run while monitoring
 * @returns {Promise<Object>} Network statistics
 */
export async function monitorNetworkDuring(page, testFunction) {
  const requests = [];
  const responses = [];

  const requestHandler = (request) => {
    requests.push({
      url: request.url(),
      method: request.method(),
      timestamp: Date.now()
    });
  };

  const responseHandler = (response) => {
    responses.push({
      url: response.url(),
      status: response.status(),
      timestamp: Date.now()
    });
  };

  page.on('request', requestHandler);
  page.on('response', responseHandler);

  try {
    await testFunction();
  } finally {
    page.off('request', requestHandler);
    page.off('response', responseHandler);
  }

  const apiRequests = requests.filter(r => r.url.includes('/api/'));
  const failedResponses = responses.filter(r => r.status >= 400);

  return {
    totalRequests: requests.length,
    apiRequests: apiRequests.length,
    failedResponses: failedResponses.length,
    requests,
    responses
  };
}

/**
 * Test data for Persian content
 */
export const PERSIAN_TEST_DATA = {
  artists: [
    'محسن یگانه',
    'ابی',
    'گوگوش',
    'شادمهر عقیلی',
    'محسن چاوشی',
    'احسان خواجه امیری',
    'بنیامین بهادری',
    'مازیار فلاحی'
  ],
  songs: [
    'بهت قول میدم',
    'عاشقانه',
    'دوست دارم',
    'خاطرات',
    'دیوونه'
  ]
};

/**
 * Generate a detailed test report
 * @param {Object} testResults - Test results object
 * @returns {string} Formatted report
 */
export function generateTestReport(testResults) {
  const report = `
=== Radio Javan E2E Test Report ===
Date: ${new Date().toISOString()}

Test Summary:
- Total Tests: ${testResults.total}
- Passed: ${testResults.passed}
- Failed: ${testResults.failed}
- Duration: ${testResults.duration}ms

API Performance:
- Average Response Time: ${testResults.avgResponseTime}ms
- Slowest Endpoint: ${testResults.slowestEndpoint}

Downloads:
- Total Downloads: ${testResults.downloads}
- Average File Size: ${testResults.avgFileSize}MB

Media Playback:
- Songs Played: ${testResults.songsPlayed}
- Videos Played: ${testResults.videosPlayed}
- Playback Errors: ${testResults.playbackErrors}

Console Errors: ${testResults.consoleErrors}
Network Errors: ${testResults.networkErrors}
`;

  return report;
}
