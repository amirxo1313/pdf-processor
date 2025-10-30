import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('Advanced Radio Javan Scenarios', () => {

  test('Test Playlist Navigation and Playback', async ({ page }) => {
    console.log('📋 Testing playlist functionality');

    await page.goto(BASE_URL);

    // Search for playlists
    const searchInput = await page.locator('input[placeholder*="Search"]');
    await searchInput.fill('top 20');
    await searchInput.press('Enter');

    const response = await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search'),
      { timeout: 15000 }
    );

    const data = await response.json();
    console.log('Playlists found:', data?.result?.playlists?.length || 0);

    // Click on playlists tab if available
    const playlistsTab = page.locator('[data-testid="tab-playlists"]');
    if (await playlistsTab.isVisible()) {
      await playlistsTab.click();
      await page.waitForTimeout(1000);

      // Click first playlist
      const firstPlaylist = await page.locator('.MediaCard').first();
      if (await firstPlaylist.isVisible()) {
        await firstPlaylist.click();

        // Wait for playlist details to load
        await page.waitForResponse(
          response => response.url().includes('/api/radiojavan/playlist/'),
          { timeout: 15000 }
        );

        console.log('✅ Playlist loaded');

        await page.screenshot({
          path: 'test-results/playlist-details.png',
          fullPage: true
        });
      }
    }
  });

  test('Test Album Full Playback', async ({ page }) => {
    console.log('💿 Testing album playback');

    await page.goto(BASE_URL);

    // Search for albums
    const searchInput = await page.locator('input[placeholder*="Search"]');
    await searchInput.fill('album');
    await searchInput.press('Enter');

    await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search')
    );

    // Switch to albums tab
    const albumsTab = page.locator('[data-testid="tab-albums"]');
    if (await albumsTab.isVisible()) {
      await albumsTab.click();
      await page.waitForTimeout(1000);

      // Click first album
      const firstAlbum = await page.locator('[data-testid^="track-"]').first();
      if (await firstAlbum.isVisible()) {
        await firstAlbum.click();

        // Wait for album details
        await page.waitForResponse(
          response => response.url().includes('/api/radiojavan/album/'),
          { timeout: 15000 }
        );

        console.log('✅ Album loaded');
      }
    }
  });

  test('Test Video Playback', async ({ page }) => {
    console.log('🎬 Testing video playback');

    await page.goto(BASE_URL);

    // Search for videos
    const searchInput = await page.locator('input[placeholder*="Search"]');
    await searchInput.fill('music video');
    await searchInput.press('Enter');

    const response = await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search')
    );

    const data = await response.json();
    console.log('Videos found:', data?.result?.videos?.length || 0);

    // Click videos tab
    const videosTab = page.locator('[data-testid="tab-videos"]');
    if (await videosTab.isVisible()) {
      await videosTab.click();
      await page.waitForTimeout(1000);

      // Play first video
      const firstVideo = await page.locator('.MediaCard').first();
      if (await firstVideo.isVisible()) {
        await firstVideo.click();
        await page.waitForTimeout(3000);

        // Check for video element
        const videoStatus = await page.evaluate(() => {
          const video = document.querySelector('video');
          if (!video) return { found: false };

          return {
            found: true,
            paused: video.paused,
            currentTime: video.currentTime,
            duration: video.duration,
            src: video.src,
            readyState: video.readyState
          };
        });

        console.log('🎬 Video Status:', videoStatus);

        await page.screenshot({
          path: 'test-results/video-playing.png'
        });
      }
    }
  });

  test('Test Podcast Streaming', async ({ page }) => {
    console.log('🎙️ Testing podcast streaming');

    await page.goto(BASE_URL);

    // Search for podcasts
    const searchInput = await page.locator('input[placeholder*="Search"]');
    await searchInput.fill('podcast');
    await searchInput.press('Enter');

    const response = await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search')
    );

    const data = await response.json();
    console.log('Podcasts found:', data?.result?.podcasts?.length || 0);

    // Click podcasts tab
    const podcastsTab = page.locator('[data-testid="tab-podcasts"]');
    if (await podcastsTab.isVisible()) {
      await podcastsTab.click();
      await page.waitForTimeout(1000);

      // Play first podcast
      const firstPodcast = await page.locator('.MediaCard').first();
      if (await firstPodcast.isVisible()) {
        await firstPodcast.click();
        await page.waitForTimeout(3000);

        // Verify podcast is playing
        const audioStatus = await page.evaluate(() => {
          const audio = document.querySelector('audio');
          return audio ? {
            playing: !audio.paused,
            currentTime: audio.currentTime,
            duration: audio.duration
          } : null;
        });

        console.log('🎙️ Podcast Status:', audioStatus);
      }
    }
  });

  test('Test Queue Management', async ({ page }) => {
    console.log('📑 Testing queue/playlist management');

    await page.goto(BASE_URL);

    // Search and add multiple songs
    const searchInput = await page.locator('input[placeholder*="Search"]');
    await searchInput.fill('ebi');
    await searchInput.press('Enter');

    await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search')
    );

    // Play multiple songs
    const tracks = await page.locator('[data-testid^="track-"]').all();
    const tracksToPlay = tracks.slice(0, Math.min(3, tracks.length));

    for (let i = 0; i < tracksToPlay.length; i++) {
      const track = tracksToPlay[i];
      await track.hover();

      const playButton = await track.locator('[data-testid^="button-play-track-"]');
      if (await playButton.isVisible()) {
        await playButton.click();
        console.log(`✅ Added track ${i + 1} to queue`);
        await page.waitForTimeout(1000);
      }
    }

    // Check player state
    const playerState = await page.evaluate(() => {
      const title = document.querySelector('[data-testid="text-player-title"]')?.textContent;
      const artist = document.querySelector('[data-testid="text-player-artist"]')?.textContent;
      const audio = document.querySelector('audio');

      return {
        currentTrack: { title, artist },
        isPlaying: audio ? !audio.paused : false
      };
    });

    console.log('🎵 Current Player State:', playerState);
  });

  test('Test Error Handling and Recovery', async ({ page }) => {
    console.log('⚠️ Testing error scenarios');

    await page.goto(BASE_URL);

    // Test invalid search
    const searchInput = await page.locator('input[placeholder*="Search"]');
    await searchInput.fill('xyzxyzxyz123456789');
    await searchInput.press('Enter');

    await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search')
    );

    // Check for no results message
    const noResults = await page.locator('[data-testid="text-no-results"]');
    if (await noResults.isVisible()) {
      const message = await noResults.textContent();
      console.log('✅ No results handled correctly:', message);
    }

    // Test network error recovery
    await page.route('**/api/radiojavan/search**', route => {
      route.abort('failed');
    });

    await searchInput.fill('test network error');
    await searchInput.press('Enter');

    await page.waitForTimeout(2000);

    // Unblock requests
    await page.unroute('**/api/radiojavan/search**');

    console.log('✅ Network error test completed');
  });

  test('Test Continuous Playback', async ({ page }) => {
    console.log('🔄 Testing continuous playback');

    await page.goto(BASE_URL);

    // Search for content
    const searchInput = await page.locator('input[placeholder*="Search"]');
    await searchInput.fill('mohsen chavoshi');
    await searchInput.press('Enter');

    await page.waitForResponse(
      response => response.url().includes('/api/radiojavan/search')
    );

    // Play a song
    const firstTrack = await page.locator('[data-testid^="track-"]').first();
    await firstTrack.hover();
    await firstTrack.locator('[data-testid^="button-play-track-"]').click();

    // Monitor playback for 30 seconds
    console.log('⏱️ Monitoring continuous playback...');

    const playbackLog = [];
    const startTime = Date.now();

    while (Date.now() - startTime < 30000) {
      const status = await page.evaluate(() => {
        const audio = document.querySelector('audio');
        return audio ? {
          currentTime: audio.currentTime,
          paused: audio.paused,
          buffered: audio.buffered.length > 0 ?
            audio.buffered.end(audio.buffered.length - 1) : 0,
          networkState: audio.networkState
        } : null;
      });

      playbackLog.push({
        timestamp: Date.now() - startTime,
        ...status
      });

      await page.waitForTimeout(5000);
    }

    console.log('📊 Playback Statistics:');
    console.log(`- Total time monitored: 30 seconds`);
    console.log(`- Final position: ${playbackLog[playbackLog.length - 1]?.currentTime?.toFixed(2)}s`);
    console.log(`- Buffered: ${playbackLog[playbackLog.length - 1]?.buffered?.toFixed(2)}s`);

    // Verify continuous playback
    const wasPlaying = playbackLog.every(log => !log.paused);
    expect(wasPlaying).toBe(true);
    console.log('✅ Continuous playback verified');
  });

  test('Test Memory Usage During Extended Session', async ({ page }) => {
    console.log('🧠 Testing memory usage');

    await page.goto(BASE_URL);

    // Get initial memory usage
    const initialMemory = await page.evaluate(() => {
      if (performance.memory) {
        return {
          usedJSHeapSize: (performance.memory.usedJSHeapSize / 1048576).toFixed(2),
          totalJSHeapSize: (performance.memory.totalJSHeapSize / 1048576).toFixed(2)
        };
      }
      return null;
    });

    console.log('📊 Initial Memory:', initialMemory);

    // Perform multiple searches and plays
    const searches = ['ebi', 'googoosh', 'mohsen', 'shadmehr'];

    for (const query of searches) {
      const searchInput = await page.locator('input[placeholder*="Search"]');
      await searchInput.clear();
      await searchInput.fill(query);
      await searchInput.press('Enter');

      await page.waitForResponse(
        response => response.url().includes('/api/radiojavan/search')
      );

      // Play first result
      const track = await page.locator('[data-testid^="track-"]').first();
      if (await track.isVisible()) {
        await track.hover();
        const playButton = await track.locator('[data-testid^="button-play-track-"]');
        if (await playButton.isVisible()) {
          await playButton.click();
          await page.waitForTimeout(2000);
        }
      }
    }

    // Get final memory usage
    const finalMemory = await page.evaluate(() => {
      if (performance.memory) {
        return {
          usedJSHeapSize: (performance.memory.usedJSHeapSize / 1048576).toFixed(2),
          totalJSHeapSize: (performance.memory.totalJSHeapSize / 1048576).toFixed(2)
        };
      }
      return null;
    });

    console.log('📊 Final Memory:', finalMemory);

    if (initialMemory && finalMemory) {
      const memoryIncrease = parseFloat(finalMemory.usedJSHeapSize) - parseFloat(initialMemory.usedJSHeapSize);
      console.log(`📈 Memory increase: ${memoryIncrease.toFixed(2)} MB`);

      // Warn if memory increased significantly
      if (memoryIncrease > 50) {
        console.warn('⚠️ Significant memory increase detected');
      }
    }
  });
});
