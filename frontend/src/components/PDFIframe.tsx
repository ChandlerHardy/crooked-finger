import React, { useState, useEffect } from 'react';
import { Loader2, FileText } from 'lucide-react';
import { pdfCache } from '../lib/pdfCache';
import { isPdf } from '../lib/pdfToImage';

interface PDFIframeProps {
  src: string;
  title?: string;
  className?: string;
  showPDFLabel?: boolean;
  onLoad?: () => void;
  preload?: boolean;
  fallbackToImage?: boolean; // Whether to try converting PDF to image as fallback
}

export function PDFIframe({ 
  src, 
  title, 
  className = "", 
  showPDFLabel = true, 
  onLoad, 
  preload = false,
  fallbackToImage = false // New prop to control PDF to image conversion
}: PDFIframeProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [cachedSrc, setCachedSrc] = useState<string>(src);
  const [isFromCache, setIsFromCache] = useState(false);
  const [displayMode, setDisplayMode] = useState<'pdf' | 'image' | 'error'>('pdf'); // Track display mode
  
  // Use ref to maintain the cached src across re-renders
  const cachedSrcRef = React.useRef<string | null>(null);
  const isLoadedRef = React.useRef(false);

  useEffect(() => {
    let isMounted = true;

    const loadContent = async () => {
      // Skip if already loaded for this source
      if (isLoadedRef.current && cachedSrcRef.current) {
        return;
      }
      
      setIsLoading(true);
      
      try {
        // Check if content is PDF and we should try to convert to image
        if (isPdf(src) && fallbackToImage) {
          // Try PDF to image conversion
          try {
            console.log('🔄 Converting PDF to image for display:', title || src);
            const { convertPdfToImage } = await import('../lib/pdfToImage');
            const imageDataUrl = await convertPdfToImage(src);
            
            if (isMounted) {
              setCachedSrc(imageDataUrl);
              cachedSrcRef.current = imageDataUrl;
              setDisplayMode('image');
              setIsLoading(false);
              isLoadedRef.current = true;
              console.log('🖼️ PDF converted to image successfully');
            }
            return;
          } catch (conversionError) {
            console.warn('⚠️ PDF to image conversion failed, falling back to PDF display:', conversionError);
            // Continue with normal PDF loading
          }
        }
        
        // Try to get cached version first
        const cached = pdfCache.getCached(src);
        if (cached) {
          if (isMounted) {
            setCachedSrc(cached);
            cachedSrcRef.current = cached;
            setIsFromCache(true);
            setDisplayMode('pdf');
            setIsLoading(false);
            isLoadedRef.current = true;
            console.log('⚡ Using cached PDF for:', title || 'PDF');
          }
          return;
        }

        // Cache the PDF if not already cached
        const cachedUrl = await pdfCache.cachePDF(src);
        if (isMounted) {
          setCachedSrc(cachedUrl);
          cachedSrcRef.current = cachedUrl;
          setIsFromCache(true);
          setDisplayMode('pdf');
          isLoadedRef.current = true;
          // Give the iframe a moment to start loading before hiding loader
          setTimeout(() => {
            if (isMounted) {
              setIsLoading(false);
            }
          }, 500);
        }
      } catch (error) {
        console.error('Error loading content:', error);
        if (isMounted) {
          setCachedSrc(src); // Fallback to original URL
          cachedSrcRef.current = src;
          setIsFromCache(false);
          setDisplayMode('error');
          setIsLoading(false);
          isLoadedRef.current = true;
        }
      }
    };

    if (preload) {
      // Preload without showing loading state
      pdfCache.cachePDF(src);
    } else {
      loadContent();
    }

    return () => {
      isMounted = false;
    };
  }, [src, title, preload, fallbackToImage]);

  // Reset state when src changes
  React.useEffect(() => {
    // Reset for new src
    isLoadedRef.current = false;
    cachedSrcRef.current = null;
    setIsFromCache(false);
    setDisplayMode('pdf');
    setCachedSrc(src);
    if (!preload) {
      setIsLoading(true);
    }
  }, [src, preload]);

  const handleLoad = () => {
    setIsLoading(false);
    isLoadedRef.current = true;
    onLoad?.();
  };

  const handleError = () => {
    console.error('Content failed to load for:', title || src);
    
    // If loading a cached blob failed, invalidate cache and try original URL
    if (cachedSrc !== src && displayMode === 'pdf') {
      console.log('🔄 Cached blob failed, trying original URL');
      if (cachedSrc.startsWith('blob:')) {
        // Need to invalidate the cache - use setTimeout to avoid dependency cycles
        setTimeout(() => {
          pdfCache.invalidate(src);
        }, 0);
      }
      setCachedSrc(src);
      setIsFromCache(false);
      // Give it one more chance
      setTimeout(() => {
        setIsLoading(false);
      }, 1000);
    } else {
      setIsLoading(false);
    }
  };

  // If it's an image, render img instead of iframe
  if (displayMode === 'image') {
    return (
      <div className="w-full h-full relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10">
            <div className="text-center">
              <Loader2 className="h-8 w-8 text-gray-400 animate-spin mx-auto mb-2" />
              <p className="text-sm text-gray-500">Converting PDF to image...</p>
            </div>
          </div>
        )}
        
        <img
          src={cachedSrc}
          alt={title}
          className={`w-full h-full object-contain ${className}`}
          onLoad={handleLoad}
          onError={handleError}
        />
        
        {showPDFLabel && (
          <div className="absolute top-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded">
            PDF Preview
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="w-full h-full relative">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10">
          <div className="text-center">
            <Loader2 className="h-8 w-8 text-gray-400 animate-spin mx-auto mb-2" />
            <p className="text-sm text-gray-500">
              {isFromCache ? 'Loading cached PDF...' : 'Loading PDF...'}
            </p>
          </div>
        </div>
      )}
      
      <iframe
        src={cachedSrc}
        title={title}
        className={`w-full h-full border-0 ${className}`}
        onLoad={handleLoad}
        onError={handleError}
      />
      
      {showPDFLabel && (
        <div className="absolute top-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded">
          PDF
        </div>
      )}
    </div>
  );
}

// Utility component for preloading PDFs
export function PDFPreloader({ urls }: { urls: string[] }) {
  React.useEffect(() => {
    // Preload first few PDFs in the background
    try {
      pdfCache.preload(urls.slice(0, 3));
    } catch (error) {
      console.warn('PDF preloader error:', error);
    }
  }, [urls]);

  return null; // This component doesn't render anything
}
