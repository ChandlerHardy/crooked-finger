/**
 * Utility functions for PDF to image conversion
 */

// Check if we're in a browser environment
const isBrowser = typeof window !== 'undefined';



/**
 * Convert a PDF URL to a JPEG data URL
 * @param pdfUrl - URL or data URL of the PDF
 * @param pageNumber - Page number to convert (default: 1)
 * @returns Promise<string> - Data URL of the converted image
 */
export const convertPdfToImage = async (pdfUrl: string, pageNumber: number = 1): Promise<string> => {
  if (!isBrowser) {
    throw new Error('PDF conversion is only available in browser environment');
  }

  // Dynamically import pdfjs-dist to avoid SSR issues
  const pdfjsLib = await import('pdfjs-dist');
  
  // Set the worker source - using local file for Next.js compatibility
  pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.min.mjs';
  
  try {
    // Fetch the PDF
    const response = await fetch(pdfUrl);
    const arrayBuffer = await response.arrayBuffer();
    
    // Load the PDF
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    
    // Get the specified page
    const page = await pdf.getPage(pageNumber);
    
    // Set up the viewport (scale factor affects image quality)
    const scale = 1.5; // Adjust as needed for quality vs performance
    const viewport = page.getViewport({ scale });
    
    // Create a canvas to render the page
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    if (!context) {
      throw new Error('Could not get canvas context');
    }
    
    canvas.height = viewport.height;
    canvas.width = viewport.width;
    
    // Render the page on the canvas
    const renderContext = {
      canvasContext: context,
      canvas: canvas,  // Add the canvas element as well
      viewport: viewport,
    };
    
    const renderTask = page.render(renderContext);
    await renderTask.promise;
    
    // Convert canvas to data URL
    return canvas.toDataURL('image/jpeg', 0.85); // 85% quality JPEG
  } catch (error) {
    console.error('Error converting PDF to image:', error);
    throw error;
  }
};

/**
 * Check if a URL is a PDF
 * @param url - The URL to check
 * @returns boolean - True if URL is a PDF
 */
export const isPdf = (url: string): boolean => {
  return url.toLowerCase().includes('.pdf') || 
         url.startsWith('data:application/pdf') ||
         url.includes('application/pdf');
};

/**
 * Convert PDF URL to image URL with caching
 * @param pdfUrl - The PDF URL to convert
 * @param cache - Optional cache object to store converted images
 * @returns Promise<string> - Image URL (cached or newly converted)
 */
export const getPdfAsImage = async (
  pdfUrl: string, 
  cache?: Map<string, string>
): Promise<string> => {
  const cacheKey = `pdf-image:${pdfUrl}`;
  
  // Check cache first if provided
  if (cache && cache.has(cacheKey)) {
    return cache.get(cacheKey)!;
  }
  
  const imageUrl = await convertPdfToImage(pdfUrl);
  
  // Store in cache if provided
  if (cache) {
    cache.set(cacheKey, imageUrl);
  }
  
  return imageUrl;
};