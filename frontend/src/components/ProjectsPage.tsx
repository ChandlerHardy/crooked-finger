import { useState, useEffect } from 'react';
import { Plus, Search, Calendar, Tag, MoreVertical, Star, FolderOpen, Image as ImageIcon } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu';
import { PDFIframe, PDFPreloader } from './PDFIframe';
import { pdfCache } from '../lib/pdfCache';
import { isPdf } from '../lib/pdfToImage';

interface Project {
  id: string;
  name: string;
  description: string;
  pattern: string;
  instructions?: string;
  images?: string[];
  status: 'planning' | 'in-progress' | 'completed';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  isFavorite: boolean;
}

interface ProjectsPageProps {
  projects: Project[];
  onCreateProject: () => void;
  onProjectClick: (project: Project) => void;
  onDeleteProject?: (projectId: string) => void;
}

export function ProjectsPage({ projects, onCreateProject, onProjectClick, onDeleteProject }: ProjectsPageProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');

  // Log cache stats in development
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('📊 PDF Cache Stats:', pdfCache.getStats());
    }
  }, [projects]);

  const getProjectThumbnail = (project: Project) => {
    if (project.images && project.images.length > 0) {
      // Look for non-PDF images first (like JPEG thumbnails of PDFs)
      const nonPdfImage = project.images.find(img => !isPdf(img));
      if (nonPdfImage) {
        return nonPdfImage;
      }
      // Fallback to first image (might be PDF)
      return project.images[0];
    }
    return null;
  };

  const isPDF = (url: string) => {
    return url.toLowerCase().includes('.pdf') || url.startsWith('data:application/pdf');
  };

  // Get PDF URLs from visible projects for preloading
  const getVisiblePDFUrls = () => {
    const visibleProjects = filteredProjects.slice(0, 12); // First two rows typically visible
    return visibleProjects
      .map(project => {
        const thumbnail = getProjectThumbnail(project);
        return thumbnail && isPDF(thumbnail) ? thumbnail : null;
      })
      .filter((url): url is string => url !== null);
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesStatus = selectedStatus === 'all' || project.status === selectedStatus;
    
    return matchesSearch && matchesStatus;
  });

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

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-border p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-medium">My Projects</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Manage your crochet patterns and projects
            </p>
          </div>
          <Button onClick={onCreateProject} className="gap-2">
            <Plus className="h-4 w-4" />
            New Project
          </Button>
        </div>

        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search projects, tags, or descriptions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 border border-input rounded-md bg-background text-foreground"
          >
            <option value="all">All Status</option>
            <option value="planning">Planning</option>
            <option value="in-progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      <div className="flex-1 p-6">
        {/* Preloader for visible PDFs */}
        <PDFPreloader urls={getVisiblePDFUrls()} />
        
        {filteredProjects.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <FolderOpen className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">
              {projects.length === 0 ? 'No projects yet' : 'No projects found'}
            </h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              {projects.length === 0 
                ? 'Create your first crochet project to get started. You can save patterns, track progress, and organize your work.'
                : 'Try adjusting your search terms or filters to find what you\'re looking for.'
              }
            </p>
            {projects.length === 0 && (
              <Button onClick={onCreateProject} className="gap-2">
                <Plus className="h-4 w-4" />
                Create Your First Project
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => {
              const thumbnail = getProjectThumbnail(project);
              return (
                <Card 
                  key={project.id} 
                  className="cursor-pointer hover:shadow-md transition-shadow overflow-hidden"
                  onClick={() => onProjectClick(project)}
                >
                  {/* Thumbnail Image */}
                  {thumbnail ? (
                    <div className="aspect-video w-full bg-muted overflow-hidden">
                      {isPDF(thumbnail) ? (
                        <PDFIframe
                          src={thumbnail + "#page=1&view=FitH"}
                          title={`${project.name} thumbnail`}
                          className="w-full h-full"
                        />
                      ) : (
                        <img
                          src={thumbnail}
                          alt={`${project.name} thumbnail`}
                          className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                          onError={(e) => {
                            // Fallback to icon if image fails to load
                            e.currentTarget.style.display = 'none';
                            const parent = e.currentTarget.parentElement;
                            if (parent) {
                              parent.innerHTML = `
                                <div class="w-full h-full flex items-center justify-center bg-gray-100">
                                  <div class="text-center">
                                    <svg class="h-8 w-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                    </svg>
                                    <p class="text-xs text-gray-500">No Image</p>
                                  </div>
                                </div>
                              `;
                            }
                          }}
                        />
                      )}
                    </div>
                  ) : (
                    <div className="aspect-video w-full bg-gray-50 flex items-center justify-center">
                      <div className="text-center">
                        <ImageIcon className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">No Images</p>
                      </div>
                    </div>
                  )}
                
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium truncate">{project.name}</h3>
                          {project.isFavorite && (
                            <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {project.description}
                        </p>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-8 w-8 p-0"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>Edit</DropdownMenuItem>
                          <DropdownMenuItem>Duplicate</DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (onDeleteProject && confirm(`Are you sure you want to delete "${project.name}"?`)) {
                                onDeleteProject(project.id);
                              }
                            }}
                          >
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex flex-wrap gap-2 mb-4">
                    <Badge className={getStatusColor(project.status)}>
                      {project.status.replace('-', ' ')}
                    </Badge>
                    <Badge variant="outline" className={getDifficultyColor(project.difficulty)}>
                      {project.difficulty}
                    </Badge>
                  </div>
                  
                  {project.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-4">
                      {project.tags.slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          <Tag className="h-3 w-3 mr-1" />
                          {tag}
                        </Badge>
                      ))}
                      {project.tags.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{project.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}
                  
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Calendar className="h-3 w-3 mr-1" />
                    Updated {project.updatedAt.toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}