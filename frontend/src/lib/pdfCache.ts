// PDF Caching System
interface CachedPDF {
  blobUrl: string;
  timestamp: number;
  loadCount: number;
}

class PDFCache {
  private cache = new Map<string, CachedPDF>();
  private maxCacheSize = 20; // Maximum number of PDFs to cache
  private cacheExpiryMs = 30 * 60 * 1000; // 30 minutes
  private cleanupInterval: NodeJS.Timeout;

  constructor() {
    // Clean up expired cache entries every 5 minutes
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 5 * 60 * 1000);
  }

  // Check if a PDF is cached and not expired
  isCached(url: string): boolean {
    const cached = this.cache.get(url);
    if (!cached) return false;

    // Check if expired
    if (Date.now() - cached.timestamp > this.cacheExpiryMs) {
      this.invalidateInternal(url);
      return false;
    }

    return true;
  }

  // Get cached PDF URL
  getCached(url: string): string | null {
    if (this.isCached(url)) {
      const cached = this.cache.get(url)!;
      cached.loadCount++;
      return cached.blobUrl;
    }
    return null;
  }

  // Cache a PDF by fetching and storing as blob
  async cachePDF(url: string): Promise<string> {
    try {
      // If already cached, return cached URL
      const cached = await this.getCached(url);
      if (cached) return cached;

      // Log the caching attempt
      console.log('🔄 Caching PDF:', url.substring(0, 100) + '...');

      // Fetch the PDF
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch PDF: ${response.statusText}`);
      }

      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);

      // Store in cache
      const cachedPDF: CachedPDF = {
        blobUrl,
        timestamp: Date.now(),
        loadCount: 1
      };

      // Enforce cache size limit
      if (this.cache.size >= this.maxCacheSize) {
        this.evictLeastUsed();
      }

      this.cache.set(url, cachedPDF);
      console.log('✅ PDF cached successfully');

      return blobUrl;
    } catch (error) {
      console.error('❌ Failed to cache PDF:', error);
      // Return original URL on failure
      return url;
    }
  }

  // Preload PDFs (useful for visible thumbnails)
  async preload(urls: string[]): Promise<void> {
    const preloadPromises = urls.slice(0, 5).map(url => this.cachePDF(url)); // Limit concurrent preloads
    await Promise.allSettled(preloadPromises);
  }

  // Invalidate a specific cache entry
  invalidateInternal(url: string): void {
    const cached = this.cache.get(url);
    if (cached) {
      try {
        URL.revokeObjectURL(cached.blobUrl);
      } catch (error) {
        console.warn('Failed to revoke blob URL:', error);
      }
      this.cache.delete(url);
    }
  }

  // Remove least recently used PDFs when cache is full
  private evictLeastUsed(): void {
    let leastUsed = '';
    let minCount = Infinity;

    for (const [url, cached] of this.cache.entries()) {
      if (cached.loadCount < minCount) {
        minCount = cached.loadCount;
        leastUsed = url;
      }
    }

    if (leastUsed) {
      console.log('🗑️ Evicting least used PDF from cache');
      this.invalidateInternal(leastUsed);
    }
  }

  // Clean up expired cache entries
  private cleanup(): void {
    const now = Date.now();
    let cleanedCount = 0;

    for (const [url, cached] of this.cache.entries()) {
      if (now - cached.timestamp > this.cacheExpiryMs) {
        this.invalidateInternal(url);
        cleanedCount++;
      }
    }

    if (cleanedCount > 0) {
      console.log(`🧹 Cleaned up ${cleanedCount} expired PDFs from cache`);
    }
  }

  // Get cache statistics
  getStats(): { size: number; totalLoadCount: number; memoryUsage: string } {
    let totalLoadCount = 0;
    for (const cached of this.cache.values()) {
      totalLoadCount += cached.loadCount;
    }

    return {
      size: this.cache.size,
      totalLoadCount,
      memoryUsage: `${this.cache.size} blob URLs in memory`
    };
  }

  // Public invalidate method for external components
  invalidate(url: string): void {
    console.log('🗑️ Explicit cache invalidation for:', url.substring(0, 50));
    this.invalidateInternal(url);
  }

  // Clear all cache (for testing or low memory situations)
  clear(): void {
    for (const [url] of this.cache.entries()) {
      this.invalidateInternal(url);
    }
    console.log('🗑️ PDF cache cleared');
  }

  // Cleanup on component unmount
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.clear();
  }
}

// Singleton instance
export const pdfCache = new PDFCache();
