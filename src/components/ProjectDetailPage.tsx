import React, { useState } from 'react';
import { ArrowLeft, Edit, Star, Upload, Image as ImageIcon, MessageCircle, Tag, MoreVertical, Download, Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ChatInterface } from './ChatInterface';

// Enhanced Image Viewer Component with Zoom & Pan
interface EnhancedImageViewerProps {
  images: ProjectImage[];
  currentIndex: number;
  onClose: () => void;
  onNavigate: (index: number) => void;
}

function EnhancedImageViewer({ images, currentIndex, onClose, onNavigate }: EnhancedImageViewerProps) {
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });
  const containerRef = React.useRef<HTMLDivElement>(null);
  const imageRef = React.useRef<HTMLImageElement>(null);

  // Reset zoom and position when image changes
  React.useEffect(() => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  }, [currentIndex]);

  // Update container size on resize
  React.useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setContainerSize({ width: rect.width, height: rect.height });
      }
    };

    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  // Handle image load to get natural size
  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setImageSize({ width: img.naturalWidth, height: img.naturalHeight });
  };

  // Calculate the fitted image dimensions
  const getFittedSize = () => {
    if (!imageSize.width || !imageSize.height || !containerSize.width || !containerSize.height) {
      return { width: 0, height: 0 };
    }

    const containerAspect = containerSize.width / containerSize.height;
    const imageAspect = imageSize.width / imageSize.height;

    if (imageAspect > containerAspect) {
      // Image is wider than container
      const width = containerSize.width * 0.9; // 90% of container
      const height = width / imageAspect;
      return { width, height };
    } else {
      // Image is taller than container
      const height = containerSize.height * 0.9; // 90% of container
      const width = height * imageAspect;
      return { width, height };
    }
  };

  // Handle mouse wheel zoom - improved version
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const zoomSpeed = 0.1;
    const delta = e.deltaY > 0 ? -zoomSpeed : zoomSpeed;
    const newScale = Math.max(0.5, Math.min(5, scale + delta));

    if (containerRef.current && imageRef.current) {
      const containerRect = containerRef.current.getBoundingClientRect();
      const imageRect = imageRef.current.getBoundingClientRect();

      // Mouse position relative to the image center
      const mouseX = e.clientX - (imageRect.left + imageRect.width / 2);
      const mouseY = e.clientY - (imageRect.top + imageRect.height / 2);

      // Calculate how much to adjust position to zoom toward mouse
      const scaleChange = newScale / scale - 1;

      setPosition(prev => ({
        x: prev.x - mouseX * scaleChange,
        y: prev.y - mouseY * scaleChange
      }));
    }

    setScale(newScale);
  };

  // Handle mouse drag pan
  const handleMouseDown = (e: React.MouseEvent) => {
    // Allow panning at any zoom level
    setIsDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Handle keyboard navigation
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft' && currentIndex > 0) onNavigate(currentIndex - 1);
      if (e.key === 'ArrowRight' && currentIndex < images.length - 1) onNavigate(currentIndex + 1);
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, images.length, onClose, onNavigate]);

  return (
    <div className="absolute inset-0 bg-black bg-opacity-90 z-50">
      <div
        ref={containerRef}
        className="relative w-full h-full flex items-center justify-center overflow-hidden"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isDragging ? 'grabbing' : (scale === 1 ? 'default' : 'grab') }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 text-white hover:text-gray-300 text-2xl bg-black bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center"
        >
          ×
        </button>

        {/* Navigation Buttons */}
        {images.length > 1 && (
          <>
            <button
              onClick={() => onNavigate(currentIndex > 0 ? currentIndex - 1 : images.length - 1)}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 text-white hover:text-gray-300 text-3xl bg-black bg-opacity-50 rounded-full w-12 h-12 flex items-center justify-center z-10"
            >
              ‹
            </button>
            <button
              onClick={() => onNavigate(currentIndex < images.length - 1 ? currentIndex + 1 : 0)}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-white hover:text-gray-300 text-3xl bg-black bg-opacity-50 rounded-full w-12 h-12 flex items-center justify-center z-10"
            >
              ›
            </button>
          </>
        )}

        {/* Zoom Reset Button */}
        {scale !== 1 && (
          <button
            onClick={() => {
              setScale(1);
              setPosition({ x: 0, y: 0 });
            }}
            className="absolute top-4 left-4 z-10 text-white hover:text-gray-300 text-sm bg-black bg-opacity-50 rounded px-3 py-1"
          >
            Reset Zoom
          </button>
        )}

        {/* Zoom Level Indicator */}
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 text-white text-sm bg-black bg-opacity-50 rounded px-3 py-1">
          {Math.round(scale * 100)}%
        </div>

        {/* Image */}
        <img
          ref={imageRef}
          src={images[currentIndex]?.url}
          alt={images[currentIndex]?.caption}
          className="select-none"
          style={{
            transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
            ...getFittedSize(),
            transition: isDragging ? 'none' : 'transform 0.1s ease-out'
          }}
          draggable={false}
          onLoad={handleImageLoad}
          onDoubleClick={() => {
            if (scale === 1) {
              setScale(2);
            } else {
              setScale(1);
              setPosition({ x: 0, y: 0 });
            }
          }}
        />

        {/* Image Info */}
        <div className="absolute bottom-4 left-4 right-4 text-white text-center bg-black bg-opacity-50 rounded-lg p-3">
          <h3 className="text-lg font-medium">{images[currentIndex]?.caption}</h3>
          <p className="text-sm text-gray-300">
            {images[currentIndex]?.uploadedAt.toLocaleDateString()} • {images[currentIndex]?.type}
          </p>
          {images.length > 1 && (
            <p className="text-xs text-gray-400 mt-1">
              {currentIndex + 1} of {images.length}
            </p>
          )}
          <div className="text-xs text-gray-400 mt-2">
            Mouse wheel to zoom • Click and drag to pan • Double-click to zoom • ESC to close
          </div>
        </div>
      </div>
    </div>
  );
}

interface Project {
  id: string;
  name: string;
  description: string;
  pattern: string;
  status: 'planning' | 'in-progress' | 'completed';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  isFavorite: boolean;
}

interface ProjectImage {
  id: string;
  url: string;
  caption: string;
  uploadedAt: Date;
  type: 'progress' | 'chart' | 'reference';
}

interface ProjectDetailPageProps {
  project: Project;
  onBack: () => void;
  onUpdateProject: (project: Project) => void;
}

export function ProjectDetailPage({ project, onBack, onUpdateProject }: ProjectDetailPageProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isEditingPattern, setIsEditingPattern] = useState(false);
  const [editedProject, setEditedProject] = useState(project);
  const [chatLoading, setChatLoading] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxIndex, setLightboxIndex] = useState(0);
  // Load images from localStorage on component mount
  const [images, setImages] = useState<ProjectImage[]>(() => {
    try {
      const savedImages = localStorage.getItem(`project-images-${project.id}`);
      if (savedImages) {
        const parsed = JSON.parse(savedImages);
        // Convert date strings back to Date objects
        return parsed.map((img: any) => ({
          ...img,
          uploadedAt: new Date(img.uploadedAt)
        }));
      }
    } catch (error) {
      console.error('Error loading saved images:', error);
    }

    // Default mock data for demonstration
    return [
      {
        id: '1',
        url: 'https://picsum.photos/400/300?random=1',
        caption: 'Starting the first round',
        uploadedAt: new Date(),
        type: 'progress'
      },
      {
        id: '2',
        url: 'https://picsum.photos/400/300?random=2',
        caption: 'Pattern chart',
        uploadedAt: new Date(),
        type: 'chart'
      }
    ];
  });

  // Project-specific chat history starts empty
  const [projectChatHistory, setProjectChatHistory] = useState([]);

  // Save images to localStorage whenever images change
  React.useEffect(() => {
    try {
      localStorage.setItem(`project-images-${project.id}`, JSON.stringify(images));
    } catch (error) {
      console.error('Error saving images to localStorage:', error);
    }
  }, [images, project.id]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planning': return 'bg-blue-100 text-blue-800';
      case 'in-progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-emerald-100 text-emerald-800';
      case 'intermediate': return 'bg-orange-100 text-orange-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleSave = () => {
    onUpdateProject(editedProject);
    setIsEditing(false);
  };

  const openLightbox = (index: number) => {
    setLightboxIndex(index);
    setLightboxOpen(true);
  };

  const handleDeleteImage = (imageId: string) => {
    setImages(prev => prev.filter(img => img.id !== imageId));
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      // Convert files to base64 for localStorage persistence
      Array.from(files).forEach((file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const newImage: ProjectImage = {
            id: Date.now().toString() + Math.random(),
            url: e.target?.result as string, // Base64 data URL
            caption: `Uploaded ${file.name}`,
            uploadedAt: new Date(),
            type: 'progress'
          };
          setImages(prev => [...prev, newImage]);
        };
        reader.readAsDataURL(file);
      });
    }
    // Clear the input so the same file can be uploaded again
    event.target.value = '';
  };

  const handleSendMessage = async (message: string) => {
    const userMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: message,
      timestamp: new Date(),
      isPattern: message.includes('ch ') || message.includes('dc') || message.includes('sc') || message.includes('tog'),
    };

    setProjectChatHistory(prev => [...prev, userMessage]);
    setChatLoading(true);

    try {
      // Create project context for the AI
      const projectContext = `Project: ${project.name}
Description: ${project.description}
Difficulty: ${project.difficulty}
Status: ${project.status}
Tags: ${project.tags.join(', ')}

Pattern:
${project.pattern || 'No pattern yet'}`;

      // Use fetch() directly for GraphQL call
      const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://150.136.38.166:8001/crooked-finger/graphql';
      const response = await fetch(graphqlUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: `
            mutation ChatWithAssistantEnhanced($message: String!, $context: String) {
              chatWithAssistantEnhanced(message: $message, context: $context) {
                message
                diagramSvg
                diagramPng
                hasPattern
              }
            }
          `,
          variables: {
            message,
            context: projectContext,
          },
        }),
      });

      const result = await response.json();

      if (result.data?.chatWithAssistantEnhanced) {
        const response = result.data.chatWithAssistantEnhanced;
        const assistantMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant' as const,
          content: response.message,
          timestamp: new Date(),
          isPattern: response.hasPattern,
          diagramSvg: response.diagramSvg,
          diagramPng: response.diagramPng,
        };
        setProjectChatHistory(prev => [...prev, assistantMessage]);
      } else if (result.errors) {
        console.error('GraphQL errors:', result.errors);
        throw new Error('GraphQL mutation failed');
      }
    } catch (error) {
      console.error('Project chat error:', error);

      // Fallback response with project context
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant' as const,
        content: `I'm having trouble connecting to the AI service right now. For your project "${project.name}", you can try asking about specific crochet techniques or pattern clarifications once the connection is restored.`,
        timestamp: new Date(),
        isPattern: false,
      };
      setProjectChatHistory(prev => [...prev, assistantMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-border p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={onBack} className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Projects
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setEditedProject(prev => ({ ...prev, isFavorite: !prev.isFavorite }))}
            >
              <Star className={`h-4 w-4 ${editedProject.isFavorite ? 'text-yellow-500 fill-yellow-500' : ''}`} />
            </Button>
            <Button variant="outline" onClick={() => setIsEditing(!isEditing)}>
              <Edit className="h-4 w-4 mr-2" />
              {isEditing ? 'Cancel' : 'Edit'}
            </Button>
            {isEditing && (
              <Button onClick={handleSave}>Save Changes</Button>
            )}
          </div>
        </div>

        {isEditing ? (
          <div className="space-y-4">
            <Input
              value={editedProject.name}
              onChange={(e) => setEditedProject(prev => ({ ...prev, name: e.target.value }))}
              className="text-xl font-medium"
              placeholder="Project name"
            />
            <Textarea
              value={editedProject.description}
              onChange={(e) => setEditedProject(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Project description"
              rows={2}
            />
          </div>
        ) : (
          <div>
            <h1 className="text-2xl font-bold mb-2">{project.name}</h1>
            <p className="text-muted-foreground mb-4">{project.description}</p>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          <Badge className={getStatusColor(project.status)}>
            {project.status.replace('-', ' ')}
          </Badge>
          <Badge variant="outline" className={getDifficultyColor(project.difficulty)}>
            {project.difficulty}
          </Badge>
          {project.tags.map((tag) => (
            <Badge key={tag} variant="secondary">
              <Tag className="h-3 w-3 mr-1" />
              {tag}
            </Badge>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 overflow-hidden">
        <Tabs defaultValue="pattern" className="h-full flex flex-col">
          <TabsList className="grid w-full grid-cols-4 flex-shrink-0">
            <TabsTrigger value="pattern">Pattern</TabsTrigger>
            <TabsTrigger value="images">Images</TabsTrigger>
            <TabsTrigger value="chat">Project Chat</TabsTrigger>
            <TabsTrigger value="notes">Notes</TabsTrigger>
          </TabsList>

          <TabsContent value="pattern" className="flex-1 mt-6 overflow-auto">
            <Card className="h-full flex flex-col">
              <CardHeader className="flex-shrink-0">
                <div className="flex items-center justify-between">
                  <CardTitle>Pattern Instructions</CardTitle>
                  <div className="flex items-center gap-2">
                    {isEditingPattern && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsEditingPattern(false)}
                      >
                        Cancel
                      </Button>
                    )}
                    <Button
                      variant={isEditingPattern ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        if (isEditingPattern) {
                          onUpdateProject(editedProject);
                        }
                        setIsEditingPattern(!isEditingPattern);
                      }}
                    >
                      <Edit className="h-4 w-4 mr-2" />
                      {isEditingPattern ? 'Save' : 'Edit Pattern'}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex-1 overflow-auto">
                {isEditingPattern ? (
                  <Textarea
                    value={editedProject.pattern}
                    onChange={(e) => setEditedProject(prev => ({ ...prev, pattern: e.target.value }))}
                    placeholder="Enter your pattern instructions here..."
                    className="font-mono text-sm h-full resize-none"
                  />
                ) : (
                  <div className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded-md h-full overflow-auto">
                    {project.pattern || 'No pattern instructions yet. Click "Edit Pattern" to add them.'}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="images" className="flex-1 mt-6 overflow-auto relative">
            <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium">Project Images</h3>
              <div>
                <input
                  type="file"
                  id="image-upload"
                  multiple
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <Button asChild>
                  <label htmlFor="image-upload" className="cursor-pointer gap-2">
                    <Upload className="h-4 w-4" />
                    Upload Images
                  </label>
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {images.map((image, index) => (
                <Card key={image.id} className="overflow-hidden">
                  <div
                    className="aspect-video bg-muted overflow-hidden cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => openLightbox(index)}
                  >
                    <img
                      src={image.url}
                      alt={image.caption}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Fallback to icon if image fails to load
                        e.currentTarget.style.display = 'none';
                        e.currentTarget.parentElement!.classList.add('flex', 'items-center', 'justify-center');
                        const icon = document.createElement('div');
                        icon.innerHTML = '<svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>';
                        e.currentTarget.parentElement!.appendChild(icon);
                      }}
                    />
                  </div>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium">{image.caption}</p>
                        <p className="text-xs text-muted-foreground">
                          {image.uploadedAt.toLocaleDateString()}
                        </p>
                        <Badge variant="outline" className="mt-2 text-xs">
                          {image.type}
                        </Badge>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => handleDeleteImage(image.id)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {images.length === 0 && (
                <div className="col-span-full text-center py-12">
                  <ImageIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No images yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Upload progress photos, charts, or reference images for your project.
                  </p>
                  <Button asChild>
                    <label htmlFor="image-upload" className="cursor-pointer gap-2">
                      <Upload className="h-4 w-4" />
                      Upload Your First Image
                    </label>
                  </Button>
                </div>
              )}
            </div>

            {/* Enhanced Image Viewer with Zoom & Pan */}
            {lightboxOpen && (
              <EnhancedImageViewer
                images={images}
                currentIndex={lightboxIndex}
                onClose={() => setLightboxOpen(false)}
                onNavigate={setLightboxIndex}
              />
            )}
            </div>
          </TabsContent>

          <TabsContent value="chat" className="flex-1 mt-6 overflow-hidden">
            <Card className="h-full flex flex-col">
              <CardHeader className="flex-shrink-0">
                <CardTitle className="flex items-center gap-2">
                  <MessageCircle className="h-5 w-5" />
                  Project Discussion
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Ask questions specific to this project. The AI will have context about your pattern and progress.
                </p>
              </CardHeader>
              <CardContent className="flex-1 min-h-0 overflow-hidden">
                <div className="h-full">
                  <ChatInterface
                    chatHistory={projectChatHistory}
                    onSendMessage={handleSendMessage}
                    loading={chatLoading}
                    hideHeader={true}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notes" className="flex-1 mt-6 overflow-auto">
            <Card className="h-full flex flex-col">
              <CardHeader className="flex-shrink-0">
                <CardTitle>Project Notes</CardTitle>
              </CardHeader>
              <CardContent className="flex-1">
                <Textarea
                  placeholder="Add your personal notes, modifications, lessons learned, etc..."
                  className="resize-none h-full"
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}