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
  const [images, setImages] = useState<ProjectImage[]>([
    // Mock data for demonstration
    {
      id: '1',
      url: '/api/placeholder/300/200',
      caption: 'Starting the first round',
      uploadedAt: new Date(),
      type: 'progress'
    },
    {
      id: '2',
      url: '/api/placeholder/300/200',
      caption: 'Pattern chart',
      uploadedAt: new Date(),
      type: 'chart'
    }
  ]);

  // Project-specific chat history starts empty
  const [projectChatHistory, setProjectChatHistory] = useState([]);

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

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      // In a real app, you'd upload to a server and get back URLs
      Array.from(files).forEach((file) => {
        const newImage: ProjectImage = {
          id: Date.now().toString() + Math.random(),
          url: URL.createObjectURL(file), // Temporary URL for demo
          caption: `Uploaded ${file.name}`,
          uploadedAt: new Date(),
          type: 'progress'
        };
        setImages(prev => [...prev, newImage]);
      });
    }
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

          <TabsContent value="images" className="flex-1 mt-6 overflow-auto">
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
              {images.map((image) => (
                <Card key={image.id} className="overflow-hidden">
                  <div className="aspect-video bg-muted flex items-center justify-center">
                    <ImageIcon className="h-8 w-8 text-muted-foreground" />
                    {/* In a real app, you'd show the actual image */}
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
                          <DropdownMenuItem className="text-destructive">
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