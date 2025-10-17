/* eslint-disable @next/next/no-img-element */
import { useState, useRef, useEffect } from 'react';
import { Search, BookOpen, Download, Heart, Eye, Plus, Trash2, Upload, Image as ImageIcon, FileText } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { PDFIframe } from './PDFIframe';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from './ui/alert-dialog';
import { PatternCreationAI } from './PatternCreationAI';

interface Pattern {
  id: string;
  name: string;
  description?: string;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  category?: string;
  tags?: string[];
  notation: string;
  instructions?: string;
  materials?: string;
  estimatedTime?: string;
  videoId?: string;
  thumbnailUrl?: string;
  images?: string[];
  isFavorite: boolean;
  views: number;
  downloads: number;
  createdAt?: Date;
}

interface PatternLibraryProps {
  savedPatterns?: Pattern[];
  onSavePattern?: (pattern: Pattern) => void;
  onDeletePattern?: (patternId: string) => void;
  onUpdatePattern?: (pattern: Pattern) => void;
  onCreateProject?: (pattern: Pattern) => void;
}

interface ViewerImage {
  id: string;
  url: string;
  caption: string;
  uploadedAt: Date;
  type: 'progress' | 'chart' | 'reference';
}

// Helper function to detect if base64 string is a PDF
const isPDF = (base64String: string): boolean => {
  // Check for data URL format
  if (base64String.startsWith('data:application/pdf')) return true;

  // Check for PDF magic number (JVBERi0 = "%PDF-" in base64)
  if (base64String.startsWith('JVBERi0')) return true;

  // Check for JPEG magic number - if it's NOT a JPEG, might be PDF
  // /9j/ is the base64 for JPEG magic bytes (0xFF 0xD8 0xFF)
  if (base64String.startsWith('/9j/')) return false; // Definitely a JPEG

  // For raw base64 without prefix, decode first few bytes to check
  try {
    const decoded = atob(base64String.substring(0, 8));
    return decoded.startsWith('%PDF');
  } catch {
    return false;
  }
};

// Helper function to ensure proper data URL format
const ensureDataUrl = (base64String: string): string => {
  // Already has data URL prefix
  if (base64String.startsWith('data:')) return base64String;

  // Detect if it's a PDF and add appropriate prefix
  if (isPDF(base64String)) {
    return `data:application/pdf;base64,${base64String}`;
  }

  // Default to JPEG for images
  return `data:image/jpeg;base64,${base64String}`;
};

// Helper component to render either image or PDF
interface MediaDisplayProps {
  src: string;
  alt: string;
  className?: string;
  onClick?: () => void;
}

function MediaDisplay({ src, alt, className, onClick }: MediaDisplayProps) {
  const dataUrl = ensureDataUrl(src);

  if (isPDF(src)) {
    return (
      <div className={`relative ${className}`} onClick={onClick}>
        <PDFIframe
          src={dataUrl}
          title={alt}
          className="w-full h-full"
          showPDFLabel={false}
          fallbackToImage={true} // Try to convert PDF to image for better performance
        />
      </div>
    );
  }

  return (
    <img
      src={dataUrl}
      alt={alt}
      className={className}
      onClick={onClick}
      draggable={false}
    />
  );
}

// Enhanced Image Viewer Component
interface EnhancedImageViewerProps {
  images: ViewerImage[];
  currentIndex: number;
  onClose: () => void;
  onNavigate: (index: number) => void;
}

function EnhancedImageViewer({ images, currentIndex, onClose, onNavigate }: EnhancedImageViewerProps) {
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  }, [currentIndex]);

  useEffect(() => {
    // Disable body scroll when lightbox is open
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    };
  }, []);

  // Add wheel event listener with passive: false to allow preventDefault
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomSpeed = 0.1;
      const delta = e.deltaY > 0 ? -zoomSpeed : zoomSpeed;
      const newScale = Math.max(0.5, Math.min(5, scale + delta));

      // Get mouse position relative to the container
      const rect = container.getBoundingClientRect();
      const mouseX = e.clientX - rect.left - rect.width / 2;
      const mouseY = e.clientY - rect.top - rect.height / 2;

      // Calculate zoom to cursor
      const scaleRatio = newScale / scale - 1;
      const newPositionX = position.x - mouseX * scaleRatio;
      const newPositionY = position.y - mouseY * scaleRatio;

      setPosition({ x: newPositionX, y: newPositionY });
      setScale(newScale);
    };

    container.addEventListener('wheel', handleWheel, { passive: false });
    return () => container.removeEventListener('wheel', handleWheel);
  }, [scale, position]);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft') onNavigate(currentIndex > 0 ? currentIndex - 1 : images.length - 1);
      if (e.key === 'ArrowRight') onNavigate(currentIndex < images.length - 1 ? currentIndex + 1 : 0);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, images.length, onClose, onNavigate]);

  const handleDoubleClick = () => {
    if (scale === 1) {
      setScale(2);
    } else {
      setScale(1);
      setPosition({ x: 0, y: 0 });
    }
  };

  const handleResetZoom = () => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  };

  return (
    <div className="absolute inset-0 bg-black bg-opacity-90 z-50">
      <div
        ref={containerRef}
        className="relative w-full h-full flex items-center justify-center overflow-hidden"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isDragging ? 'grabbing' : (scale === 1 ? 'default' : 'grab') }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 text-white hover:text-gray-300 text-2xl bg-black bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center"
          aria-label="Close viewer"
        >
          ×
        </button>

        {/* Navigation buttons */}
        {images.length > 1 && (
          <>
            <button
              onClick={() => onNavigate(currentIndex > 0 ? currentIndex - 1 : images.length - 1)}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 text-white hover:text-gray-300 text-3xl bg-black bg-opacity-50 rounded-full w-12 h-12 flex items-center justify-center z-10"
              aria-label="Previous image"
            >
              ‹
            </button>
            <button
              onClick={() => onNavigate(currentIndex < images.length - 1 ? currentIndex + 1 : 0)}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-white hover:text-gray-300 text-3xl bg-black bg-opacity-50 rounded-full w-12 h-12 flex items-center justify-center z-10"
              aria-label="Next image"
            >
              ›
            </button>
          </>
        )}

        {/* Zoom Reset Button */}
        {scale !== 1 && (
          <button
            onClick={handleResetZoom}
            className="absolute top-4 left-4 z-10 text-white hover:text-gray-300 text-sm bg-black bg-opacity-50 rounded px-3 py-1"
          >
            Reset Zoom
          </button>
        )}

        {/* Zoom level indicator */}
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 text-white text-sm bg-black bg-opacity-50 rounded px-3 py-1">
          {Math.round(scale * 100)}%
        </div>

        {/* Image counter */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white text-sm bg-black/50 px-3 py-1 rounded z-10">
          {currentIndex + 1} / {images.length}
        </div>

        {/* Image or PDF */}
        {isPDF(images[currentIndex]?.url) ? (
          <div className="max-w-[90vw] max-h-[90vh] w-full h-full flex items-center justify-center">
            <PDFIframe
              src={ensureDataUrl(images[currentIndex]?.url)}
              title={`PDF preview - page ${currentIndex + 1}`}
              className="max-w-[800px] max-h-[90vh]"
              showPDFLabel={false}
              fallbackToImage={true} // Try to convert PDF to image for better performance
            />
          </div>
        ) : (
          <img
            src={ensureDataUrl(images[currentIndex]?.url)}
            alt={images[currentIndex]?.caption}
            className="max-w-[90vw] max-h-[90vh] object-contain select-none"
            style={{
              transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
              transition: isDragging ? 'none' : 'transform 0.1s ease-out',
            }}
            draggable={false}
            onDoubleClick={handleDoubleClick}
          />
        )}
      </div>
    </div>
  );
}



export function PatternLibrary({ savedPatterns = [], onSavePattern, onDeletePattern, onUpdatePattern, onCreateProject }: PatternLibraryProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedPattern, setSelectedPattern] = useState<Pattern | null>(null);
  const [showNewPatternDialog, setShowNewPatternDialog] = useState(false);
  const [patternToDelete, setPatternToDelete] = useState<Pattern | null>(null);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxIndex, setLightboxIndex] = useState(0);
  const [newPattern, setNewPattern] = useState({
    name: '',
    description: '',
    difficulty: 'beginner' as 'beginner' | 'intermediate' | 'advanced',
    category: 'motifs',
    tags: '',
    notation: '',
    instructions: '',
    materials: '',
    estimatedTime: '',
    thumbnailUrl: '',
    images: '',
  });
  const [activeTab, setActiveTab] = useState('manual'); // Track which tab is active
  const fileInputRef = useRef<HTMLInputElement>(null);
  const galleryFileInputRef = useRef<HTMLInputElement>(null);

  const categories = ['all', 'motifs', 'borders', 'stitches', 'edgings', 'flowers', 'youtube-import'];
  const difficulties = ['all', 'beginner', 'intermediate', 'advanced'];

  // Use only saved patterns from backend (no mock data)
  const allPatterns = savedPatterns;

  const filteredPatterns = allPatterns.filter(pattern => {
    const matchesSearch = pattern.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (pattern.description?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                         (pattern.tags || []).some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || pattern.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === 'all' || pattern.difficulty === selectedDifficulty;
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-emerald-100 text-emerald-800';
      case 'intermediate': return 'bg-orange-100 text-orange-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleThumbnailUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (event) => {
          if (event.target?.result) {
            setNewPattern({ ...newPattern, thumbnailUrl: event.target.result as string });
          }
        };
        reader.readAsDataURL(file);
      } else if (file.type === 'application/pdf') {
        // Convert PDF to JPEG for thumbnail
        try {
          const { convertPdfToImage } = await import('../lib/pdfToImage');
          const pdfDataUrl = URL.createObjectURL(file);
          const imageDataUrl = await convertPdfToImage(pdfDataUrl);
          
          // Clean up object URL
          URL.revokeObjectURL(pdfDataUrl);
          
          setNewPattern({ ...newPattern, thumbnailUrl: imageDataUrl });
        } catch (error) {
          console.error('Error converting PDF thumbnail to image:', error);
          // Fallback to trying to save the PDF as-is if conversion fails
          const reader = new FileReader();
          reader.onload = (event) => {
            if (event.target?.result) {
              setNewPattern({ ...newPattern, thumbnailUrl: event.target.result as string });
            }
          };
          reader.readAsDataURL(file);
        }
      }
    }
  };

  const handleSaveNewPattern = () => {
    if (!newPattern.name.trim() || !newPattern.notation.trim()) {
      alert('Please provide at least a pattern name and notation');
      return;
    }

    const pattern: Pattern = {
      id: Date.now().toString(),
      name: newPattern.name,
      description: newPattern.description || undefined,
      difficulty: newPattern.difficulty,
      category: newPattern.category,
      tags: newPattern.tags ? newPattern.tags.split(',').map(t => t.trim()) : [],
      notation: newPattern.notation,
      instructions: newPattern.instructions || undefined,
      materials: newPattern.materials || undefined,
      estimatedTime: newPattern.estimatedTime || undefined,
      thumbnailUrl: newPattern.thumbnailUrl || undefined,
      isFavorite: false,
      views: 0,
      downloads: 0,
      createdAt: new Date(),
    };

    if (onSavePattern) {
      onSavePattern(pattern);
    }

    // Reset form
    setNewPattern({
      name: '',
      description: '',
      difficulty: 'beginner',
      category: 'motifs',
      tags: '',
      notation: '',
      instructions: '',
      materials: '',
      estimatedTime: '',
      thumbnailUrl: '',
      images: '',
    });
    setShowNewPatternDialog(false);
  };

  const handleDeletePattern = () => {
    if (patternToDelete && onDeletePattern) {
      onDeletePattern(patternToDelete.id);
      if (selectedPattern?.id === patternToDelete.id) {
        setSelectedPattern(null);
      }
    }
    setPatternToDelete(null);
  };

  const handleGalleryUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && selectedPattern) {
      for (const file of Array.from(files)) {
        // Handle images directly, but convert PDFs to images first
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = (event) => {
            if (event.target?.result && selectedPattern) {
              const updatedPattern = {
                ...selectedPattern,
                images: [...(selectedPattern.images || []), event.target.result as string],
              };
              setSelectedPattern(updatedPattern);
              if (onUpdatePattern) {
                onUpdatePattern(updatedPattern);
              }
            }
          };
          reader.readAsDataURL(file);
        } else if (file.type === 'application/pdf') {
          // Convert PDF to JPEG before storing
          try {
            const { convertPdfToImage } = await import('../lib/pdfToImage');
            const arrayBuffer = await file.arrayBuffer();
            // Create a data URL for the PDF first to pass to convertPdfToImage
            const pdfDataUrl = URL.createObjectURL(file);
            const imageDataUrl = await convertPdfToImage(pdfDataUrl);
            
            // Clean up object URL
            URL.revokeObjectURL(pdfDataUrl);
            
            if (selectedPattern) {
              const updatedPattern = {
                ...selectedPattern,
                images: [...(selectedPattern.images || []), imageDataUrl],
              };
              setSelectedPattern(updatedPattern);
              if (onUpdatePattern) {
                onUpdatePattern(updatedPattern);
              }
            }
          } catch (error) {
            console.error('Error converting PDF to image:', error);
            // Fallback to trying to save the PDF as-is if conversion fails
            const reader = new FileReader();
            reader.onload = (event) => {
              if (event.target?.result && selectedPattern) {
                const updatedPattern = {
                  ...selectedPattern,
                  images: [...(selectedPattern.images || []), event.target.result as string],
                };
                setSelectedPattern(updatedPattern);
                if (onUpdatePattern) {
                  onUpdatePattern(updatedPattern);
                }
              }
            };
            reader.readAsDataURL(file);
          }
        }
      }
    }
    if (galleryFileInputRef.current) {
      galleryFileInputRef.current.value = '';
    }
  };

  const handleDeleteImage = (index: number) => {
    if (selectedPattern) {
      const imageToDelete = selectedPattern.images?.[index];
      const updatedPattern = {
        ...selectedPattern,
        images: (selectedPattern.images || []).filter((_, i) => i !== index),
        // If deleting the thumbnail, clear it
        thumbnailUrl: selectedPattern.thumbnailUrl === imageToDelete ? undefined : selectedPattern.thumbnailUrl,
      };
      setSelectedPattern(updatedPattern);
      if (onUpdatePattern) {
        onUpdatePattern(updatedPattern);
      }
    }
  };

  const handleSetThumbnail = (index: number) => {
    if (selectedPattern && selectedPattern.images?.[index]) {
      const updatedPattern = {
        ...selectedPattern,
        thumbnailUrl: selectedPattern.images[index],
      };
      setSelectedPattern(updatedPattern);
      if (onUpdatePattern) {
        onUpdatePattern(updatedPattern);
      }
    }
  };

  const openLightbox = (index: number) => {
    setLightboxIndex(index);
    setLightboxOpen(true);
  };

  // If a pattern is selected, show detail view
  if (selectedPattern) {
    return (
      <div className="h-full flex flex-col overflow-hidden relative">
        <div className="border-b border-border p-6">
          <Button
            variant="ghost"
            onClick={() => setSelectedPattern(null)}
            className="mb-4"
          >
            ← Back to Library
          </Button>
          <h2 className="text-2xl font-medium">{selectedPattern.name}</h2>
          {selectedPattern.description && (
            <p className="text-muted-foreground mt-2">{selectedPattern.description}</p>
          )}
        </div>

        <div className="flex-1 overflow-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Image Gallery */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">Images</h3>
                  <div className="flex gap-2">
                    <input
                      ref={galleryFileInputRef}
                      type="file"
                      accept="image/*,application/pdf"
                      multiple
                      onChange={handleGalleryUpload}
                      className="hidden"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => galleryFileInputRef.current?.click()}
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Add Images
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {(selectedPattern.images || []).length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <ImageIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No images yet. Upload some to get started!</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {(selectedPattern.images || []).map((image, index) => (
                      <div key={index} className="relative group">
                        <MediaDisplay
                          src={image}
                          alt={`Pattern image ${index + 1}`}
                          className="w-full aspect-square object-cover rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                          onClick={() => openLightbox(index)}
                        />
                        {isPDF(image) && (
                          <div className="absolute top-2 left-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded pointer-events-none">
                            PDF
                          </div>
                        )}
                        <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                          <Button
                            variant="secondary"
                            size="icon"
                            className="h-8 w-8 bg-background/90 hover:bg-background pointer-events-auto"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSetThumbnail(index);
                            }}
                            title="Set as thumbnail"
                          >
                            <ImageIcon className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="destructive"
                            size="icon"
                            className="h-8 w-8 pointer-events-auto"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteImage(index);
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                        {selectedPattern.thumbnailUrl === image && (
                          <div className="absolute bottom-2 left-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded pointer-events-none">
                            Thumbnail
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Metadata */}
            <div className="flex flex-wrap gap-2">
              {selectedPattern.difficulty && (
                <Badge className={getDifficultyColor(selectedPattern.difficulty)}>
                  {selectedPattern.difficulty}
                </Badge>
              )}
              {selectedPattern.category && (
                <Badge variant="outline">{selectedPattern.category}</Badge>
              )}
              {selectedPattern.tags?.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>

            {/* Pattern Details */}
            <Card>
              <CardHeader>
                <h3 className="font-medium">Pattern Notation</h3>
              </CardHeader>
              <CardContent>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <pre className="text-sm font-mono whitespace-pre-wrap break-words">
                    {selectedPattern.notation}
                  </pre>
                </div>
              </CardContent>
            </Card>

            {selectedPattern.instructions && (
              <Card>
                <CardHeader>
                  <h3 className="font-medium">Instructions</h3>
                </CardHeader>
                <CardContent>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {selectedPattern.instructions}
                  </p>
                </CardContent>
              </Card>
            )}

            {selectedPattern.materials && (
              <Card>
                <CardHeader>
                  <h3 className="font-medium">Materials</h3>
                </CardHeader>
                <CardContent>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {selectedPattern.materials}
                  </p>
                </CardContent>
              </Card>
            )}

            {selectedPattern.estimatedTime && (
              <Card>
                <CardHeader>
                  <h3 className="font-medium">Estimated Time</h3>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">{selectedPattern.estimatedTime}</p>
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <Button variant="outline" className="flex-1">
                <Heart className="h-4 w-4 mr-2" />
                Add to Favorites
              </Button>
              <Button variant="outline" className="flex-1">
                <Download className="h-4 w-4 mr-2" />
                Download Pattern
              </Button>
              <Button
                variant="destructive"
                className="flex-1"
                onClick={() => setPatternToDelete(selectedPattern)}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Pattern
              </Button>
              <Button
                className="flex-1"
                onClick={() => {
                  if (onCreateProject && selectedPattern) {
                    onCreateProject(selectedPattern);
                  }
                }}
              >
                Start Project
              </Button>
            </div>
          </div>
        </div>

        {/* Image Lightbox for detail view */}
        {lightboxOpen && selectedPattern.images && selectedPattern.images.length > 0 && (
          <EnhancedImageViewer
            images={selectedPattern.images.map((img, i) => ({
              id: i.toString(),
              url: img,
              caption: `Image ${i + 1} of ${selectedPattern.name}`,
              uploadedAt: new Date(),
              type: 'reference' as const,
            }))}
            currentIndex={lightboxIndex}
            onClose={() => setLightboxOpen(false)}
            onNavigate={setLightboxIndex}
          />
        )}
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="border-b border-border p-6 flex-shrink-0">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h2 className="text-xl font-medium flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Pattern Library
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              Discover and save crochet patterns with AI translations
            </p>
          </div>
          <Button onClick={() => setShowNewPatternDialog(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Pattern
          </Button>
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="relative flex-1 min-w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search patterns, tags, or techniques..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-input rounded-md bg-background text-foreground min-w-32"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
              </option>
            ))}
          </select>
          
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="px-3 py-2 border border-input rounded-md bg-background text-foreground min-w-32"
          >
            {difficulties.map(difficulty => (
              <option key={difficulty} value={difficulty}>
                {difficulty === 'all' ? 'All Levels' : difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {filteredPatterns.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <BookOpen className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">No patterns found</h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Try adjusting your search terms or filters to find what you&apos;re looking for.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredPatterns.map((pattern) => (
              <Card key={pattern.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-4">
                  <div className="flex items-start gap-4">
                    {/* Thumbnail */}
                    <div className="w-[120px] h-[120px] flex-shrink-0 rounded-lg overflow-hidden bg-muted flex items-center justify-center relative">
                      {pattern.thumbnailUrl ? (
                        <>
                          <MediaDisplay
                            src={pattern.thumbnailUrl}
                            alt={pattern.name}
                            className="w-full h-full object-cover"
                          />
                          {isPDF(pattern.thumbnailUrl) && (
                            <div className="absolute top-1 right-1 bg-primary text-primary-foreground text-xs px-1.5 py-0.5 rounded">
                              PDF
                            </div>
                          )}
                        </>
                      ) : (
                        <ImageIcon className="h-10 w-10 text-muted-foreground" />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-medium">{pattern.name}</h3>
                        {pattern.isFavorite && (
                          <Heart className="h-4 w-4 text-red-500 fill-red-500" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {pattern.description}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {pattern.difficulty && (
                          <Badge className={getDifficultyColor(pattern.difficulty)}>
                            {pattern.difficulty}
                          </Badge>
                        )}
                        {pattern.category && (
                          <Badge variant="outline">{pattern.category}</Badge>
                        )}
                        {pattern.tags?.slice(0, 2).map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="pt-0">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Notation:</label>
                      <div className="mt-1 p-3 bg-muted/50 rounded-lg max-h-24 overflow-hidden">
                        <code className="text-sm font-mono line-clamp-3">{pattern.notation}</code>
                      </div>
                    </div>

                    {pattern.instructions && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Instructions:</label>
                        <p className="mt-1 text-sm leading-relaxed line-clamp-2">{pattern.instructions}</p>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between pt-2 border-t border-border">
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Eye className="h-3 w-3" />
                          {pattern.views}
                        </span>
                        <span className="flex items-center gap-1">
                          <Download className="h-3 w-3" />
                          {pattern.downloads}
                        </span>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setPatternToDelete(pattern)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => setSelectedPattern(pattern)}
                        >
                          View Details
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* New Pattern Dialog */}
      <Dialog open={showNewPatternDialog} onOpenChange={setShowNewPatternDialog}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add New Pattern</DialogTitle>
          </DialogHeader>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="manual">Manual</TabsTrigger>
              <TabsTrigger value="ai">AI Assistant</TabsTrigger>
            </TabsList>

            <TabsContent value="manual" className="space-y-4 py-4">
            <div>
              <Label htmlFor="name" className="mb-2 block">Pattern Name *</Label>
              <Input
                id="name"
                value={newPattern.name}
                onChange={(e) => setNewPattern({ ...newPattern, name: e.target.value })}
                placeholder="e.g., Granny Square"
              />
            </div>

            <div>
              <Label htmlFor="description" className="mb-2 block">Description</Label>
              <Textarea
                id="description"
                value={newPattern.description}
                onChange={(e) => setNewPattern({ ...newPattern, description: e.target.value })}
                placeholder="Brief description of the pattern"
                rows={2}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="difficulty" className="mb-2 block">Difficulty</Label>
                <select
                  id="difficulty"
                  value={newPattern.difficulty}
                  onChange={(e) => setNewPattern({ ...newPattern, difficulty: e.target.value as 'beginner' | 'intermediate' | 'advanced' })}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div>
                <Label htmlFor="category" className="mb-2 block">Category</Label>
                <select
                  id="category"
                  value={newPattern.category}
                  onChange={(e) => setNewPattern({ ...newPattern, category: e.target.value })}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                >
                  <option value="motifs">Motifs</option>
                  <option value="borders">Borders</option>
                  <option value="stitches">Stitches</option>
                  <option value="edgings">Edgings</option>
                  <option value="flowers">Flowers</option>
                  <option value="youtube-import">YouTube Import</option>
                </select>
              </div>
            </div>

            <div>
              <Label htmlFor="tags" className="mb-2 block">Tags (comma-separated)</Label>
              <Input
                id="tags"
                value={newPattern.tags}
                onChange={(e) => setNewPattern({ ...newPattern, tags: e.target.value })}
                placeholder="e.g., square, classic, afghan"
              />
            </div>

            <div>
              <Label htmlFor="notation" className="mb-2 block">Pattern Notation *</Label>
              <Textarea
                id="notation"
                value={newPattern.notation}
                onChange={(e) => setNewPattern({ ...newPattern, notation: e.target.value })}
                placeholder="Ch 4, join with sl st to form ring. R1: Ch 3, 2 dc in ring..."
                rows={4}
              />
            </div>

            <div>
              <Label htmlFor="instructions" className="mb-2 block">Instructions</Label>
              <Textarea
                id="instructions"
                value={newPattern.instructions}
                onChange={(e) => setNewPattern({ ...newPattern, instructions: e.target.value })}
                placeholder="Detailed step-by-step instructions"
                rows={4}
              />
            </div>

            <div>
              <Label htmlFor="materials" className="mb-2 block">Materials</Label>
              <Textarea
                id="materials"
                value={newPattern.materials}
                onChange={(e) => setNewPattern({ ...newPattern, materials: e.target.value })}
                placeholder="Yarn weight, hook size, other supplies"
                rows={2}
              />
            </div>

            <div>
              <Label htmlFor="estimatedTime" className="mb-2 block">Estimated Time</Label>
              <Input
                id="estimatedTime"
                value={newPattern.estimatedTime}
                onChange={(e) => setNewPattern({ ...newPattern, estimatedTime: e.target.value })}
                placeholder="e.g., 2 hours"
              />
            </div>

            <div>
              <Label htmlFor="thumbnail" className="mb-2 block">Thumbnail Image (Optional)</Label>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,application/pdf"
                onChange={handleThumbnailUpload}
                className="hidden"
              />
              <div className="flex items-center gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="flex-shrink-0"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Image
                </Button>
                {newPattern.thumbnailUrl && (
                  <div className="flex items-center gap-2">
                    <img
                      src={newPattern.thumbnailUrl}
                      alt="Thumbnail preview"
                      className="w-16 h-16 object-cover rounded border"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setNewPattern({ ...newPattern, thumbnailUrl: '' })}
                    >
                      Remove
                    </Button>
                  </div>
                )}
              </div>
            </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNewPatternDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSaveNewPattern}>
                  Save Pattern
                </Button>
              </DialogFooter>
            </TabsContent>

            <TabsContent value="ai" forceMount className={activeTab !== 'ai' ? 'hidden' : ''}>
              {/* Keep AI component mounted to preserve chat history - use forceMount prop */}
              <PatternCreationAI
                onPatternExtracted={(data) => {
                  console.log('🎯 Pattern data extracted from AI:', data);
                  // Auto-populate form fields from AI extraction
                  setNewPattern(prev => {
                    // Merge new images with existing images
                    const existingImages = prev.images ? (typeof prev.images === 'string' ? JSON.parse(prev.images) : prev.images) : [];
                    const newImages = data.images || [];
                    const allImages = [...existingImages, ...newImages];

                    return {
                      ...prev,
                      // Use extracted data, but don't override if extraction returned undefined
                      name: data.name || prev.name,
                      notation: data.notation || prev.notation,
                      instructions: data.instructions || prev.instructions,
                      difficulty: (data.difficulty as 'beginner' | 'intermediate' | 'advanced') || prev.difficulty,
                      materials: data.materials || prev.materials,
                      estimatedTime: data.estimatedTime || prev.estimatedTime,
                      thumbnailUrl: data.images?.[0] || prev.thumbnailUrl,
                      images: allImages.length > 0 ? JSON.stringify(allImages) : prev.images,
                    };
                  });
                }}
              />
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!patternToDelete} onOpenChange={() => setPatternToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Pattern</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{patternToDelete?.name}&quot;? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeletePattern} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}