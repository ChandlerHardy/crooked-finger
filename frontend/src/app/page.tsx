'use client';

import { useState, useEffect } from 'react';
import { fetchWithAuth } from '../lib/apollo-client';
import { Navigation } from '../components/Navigation';
import { HomePage } from '../components/HomePage';
import { ChatInterface } from '../components/ChatInterface';
import { ProjectsPage } from '../components/ProjectsPage';
import { ProjectDetailPage } from '../components/ProjectDetailPage';
import { PatternLibrary } from '../components/PatternLibrary';
import AIUsageDashboardComponent from '../components/AIUsageDashboard';
import { YouTubeTest } from '../components/YouTubeTest';
import { AuthModal } from '../components/AuthModal';
import { AIModelSelector } from '../components/AIModelSelector';
import { ConversationList } from '../components/ConversationList';
import { GET_PROJECTS, GET_CHAT_MESSAGES } from '../lib/graphql/queries';
import { CREATE_PROJECT, UPDATE_PROJECT, DELETE_PROJECT } from '../lib/graphql/mutations';

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

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isPattern?: boolean;
  diagramSvg?: string;
  diagramPng?: string;
}

interface ChatConversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

interface SavedPattern {
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

export default function Home() {
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [savedPatterns, setSavedPatterns] = useState<SavedPattern[]>([]);
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [user, setUser] = useState<{ id: string; username: string; email: string } | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Load auth state from localStorage on mount
  useEffect(() => {
    const loadAuthState = () => {
      try {
        const storedToken = localStorage.getItem('crooked-finger-token');
        const storedUser = localStorage.getItem('crooked-finger-user');

        if (storedToken && storedUser) {
          setAuthToken(storedToken);
          setUser(JSON.parse(storedUser));
          
        }
      } catch (error) {
        console.error('Error loading auth state:', error);
      }
    };
    loadAuthState();
  }, []);

  // Fetch patterns/projects from backend
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [projectsData, setProjectsData] = useState<any>(null);
  const [projectsLoading, setProjectsLoading] = useState(false);
  
  const fetchProjects = async () => {
    setProjectsLoading(true);
    try {
      console.log('🔄 Fetching projects from backend...');
      const response = await fetchWithAuth(GET_PROJECTS);
      console.log('📋 Backend response:', response);
      setProjectsData(response.data);
      console.log('📊 Projects data set:', response.data);
    } catch (error) {
      console.error('❌ Error fetching projects:', error);
    } finally {
      setProjectsLoading(false);
    }
  };
  
  // Load projects on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  
  // Convert backend projects to SavedPattern format
  useEffect(() => {
    if (projectsData?.projects) {
      // Filter for patterns (projects without notes)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const patterns = projectsData.projects
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .filter((project: any) => !project.notes || project.notes.trim() === '')
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .map((project: any) => ({
          id: project.id.toString(),
          name: project.name,
          description: project.translatedText || '',
          difficulty: project.difficultyLevel as 'beginner' | 'intermediate' | 'advanced',
          category: 'imported',
          tags: [],
          notation: project.patternText || '',
          instructions: project.translatedText || '',
          materials: project.yarnWeight || '',
          estimatedTime: project.estimatedTime || '',
          images: project.imageData ? JSON.parse(project.imageData) : [],
          isFavorite: false,
          views: 0,
          downloads: 0,
          createdAt: new Date(project.createdAt),
        }));
      setSavedPatterns(patterns);
    }
  }, [projectsData]);
  
  // For projects (with notes)
  useEffect(() => {
    if (projectsData?.projects) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const userProjects = projectsData.projects
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .filter((project: any) => project.notes && project.notes.trim() !== '')
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .map((project: any) => ({
          id: project.id.toString(),
          name: project.name,
          description: project.notes || '',
          pattern: project.patternText || '',
          status: project.isCompleted ? 'completed' as const : 'in-progress' as const,
          difficulty: project.difficultyLevel as 'beginner' | 'intermediate' | 'advanced',
          tags: [],
          createdAt: new Date(project.createdAt),
          updatedAt: new Date(project.updatedAt),
          isFavorite: false,
        }));
      setProjects(userProjects);
    }
  }, [projectsData]);
  // const [chatWithAssistant, { loading: chatLoading }] = useMutation<
  //   ChatWithAssistantResponse,
  //   ChatWithAssistantVariables
  // >(CHAT_WITH_ASSISTANT);

  // GraphQL mutations
  // GraphQL mutations using fetch
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const createProjectMutation = async (variables: any) => {
    const response = await fetchWithAuth(CREATE_PROJECT, variables);
    return response.data;
  };
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const updateProjectMutation = async (variables: any) => {
    const response = await fetchWithAuth(UPDATE_PROJECT, variables);
    return response.data;
  };
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const deleteProjectMutation = async (variables: any) => {
    const response = await fetchWithAuth(DELETE_PROJECT, variables);
    return response.data;
  };
  
  // Note: Conversations will be implemented with proper backend integration
  // For now, keeping this as-is until we add conversation queries
  const loadConversations = () => {
    // Check if we're in browser environment
    if (typeof window === 'undefined') return;
    
    try {
      const stored = localStorage.getItem('crooked-finger-conversations');
      if (stored) {
        const parsed = JSON.parse(stored) as ChatConversation[];
        const conversationsWithDates = parsed.map((conv) => ({
          ...conv,
          createdAt: conv.createdAt ? new Date(conv.createdAt) : new Date(),
          updatedAt: conv.updatedAt ? new Date(conv.updatedAt) : new Date(),
          messages: conv.messages.map((msg) => ({
            ...msg,
            timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
          })),
        }));
        setConversations(conversationsWithDates);

        // Set most recent conversation as active
        if (conversationsWithDates.length > 0) {
          setActiveConversationId(conversationsWithDates[0].id);
        }
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };
  
  // Load conversations only on client side
  useEffect(() => {
    loadConversations();
  }, []);

  const [projects, setProjects] = useState<Project[]>([]);

  const handleCreateNewChat = () => {
    const newConversation: ChatConversation = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setConversations(prev => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
    setCurrentPage('chat');
  };

  const handleOpenConversation = (conversationId: string) => {
    setActiveConversationId(conversationId);
    setCurrentPage('chat');
  };

  const handleSendMessage = async (message: string, images?: string[]) => {
    // Create new conversation if none exists or none is active
    let conversationId = activeConversationId;
    if (!conversationId) {
      const newConversation: ChatConversation = {
        id: Date.now().toString(),
        title: message.slice(0, 50) + (message.length > 50 ? '...' : ''),
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      setConversations(prev => [newConversation, ...prev]);
      conversationId = newConversation.id;
      setActiveConversationId(conversationId);
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      isPattern: message.includes('ch ') || message.includes('dc') || message.includes('sc') || message.includes('tog'),
    };

    // Update conversation with new message
    setConversations(prev => prev.map(conv => {
      if (conv.id === conversationId) {
        // Update title if this is the first message
        const title = conv.messages.length === 0
          ? message.slice(0, 50) + (message.length > 50 ? '...' : '')
          : conv.title;

        return {
          ...conv,
          title,
          messages: [...conv.messages, userMessage],
          updatedAt: new Date(),
        };
      }
      return conv;
    }));

    setChatLoading(true);

    try {
      // Use fetch() directly for GraphQL call
      const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://150.136.38.166:8001/crooked-finger/graphql';

      // Prepare variables with optional image data
      const variables: Record<string, unknown> = {
        message,
        context: 'crochet_pattern_assistant',
      };

      // Convert images array to JSON string (matching iOS implementation)
      if (images && images.length > 0) {
        const base64Images = images.map(img => {
          // Remove data URL prefix (e.g., "data:image/png;base64,")
          return img.includes(',') ? img.split(',')[1] : img;
        });
        // Send as JSON string, not array - this matches iOS
        variables.imageData = JSON.stringify(base64Images);
      }

      const response = await fetch(graphqlUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
        },
        body: JSON.stringify({
          query: `
            mutation ChatWithAssistantEnhanced($message: String!, $context: String, $imageData: String) {
              chatWithAssistantEnhanced(message: $message, context: $context, imageData: $imageData) {
                message
                diagramSvg
                diagramPng
                hasPattern
              }
            }
          `,
          variables,
        }),
      });

      const result = await response.json();

      if (result.data?.chatWithAssistantEnhanced) {
        const response = result.data.chatWithAssistantEnhanced;
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: response.message,
          timestamp: new Date(),
          isPattern: response.hasPattern,
          diagramSvg: response.diagramSvg,
          diagramPng: response.diagramPng,
        };

        // Update conversation with assistant response
        setConversations(prev => prev.map(conv => {
          if (conv.id === conversationId) {
            return {
              ...conv,
              messages: [...conv.messages, assistantMessage],
              updatedAt: new Date(),
            };
          }
          return conv;
        }));
      } else if (result.errors) {
        console.error('GraphQL errors:', result.errors);
        console.error('Full error details:', JSON.stringify(result.errors, null, 2));
        throw new Error(result.errors[0]?.message || 'GraphQL mutation not available');
      }
    } catch (error) {
      console.error('Chat error:', error);

      // Fallback to mock response if backend mutation isn't available yet
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: generateAIResponse(message),
        timestamp: new Date(),
        isPattern: true,
      };

      // Update conversation with assistant response
      setConversations(prev => prev.map(conv => {
        if (conv.id === conversationId) {
          return {
            ...conv,
            messages: [...conv.messages, assistantMessage],
            updatedAt: new Date(),
          };
        }
        return conv;
      }));
    } finally {
      setChatLoading(false);
    }
  };

  const generateAIResponse = (userMessage: string): string => {
    if (userMessage.toLowerCase().includes('sc2tog')) {
      return "'sc2tog' means 'single crochet 2 together' - it's a decrease stitch that combines two stitches into one.";
    }
    if (userMessage.toLowerCase().includes('pattern')) {
      return "I can help translate that crochet pattern! The notation you've shared uses standard abbreviations. Let me break it down into clear, step-by-step instructions for you.";
    }
    return "I'm here to help with your crochet questions! Feel free to paste any pattern notation, and I'll translate it into easy-to-follow instructions.";
  };

  const handleCreateProject = async () => {
    // For now, just log that create was clicked
    // In a real app, this would open a create project modal/form
    console.log('Create new project');
  };

  const handleProjectClick = (project: Project) => {
    setSelectedProject(project);
    setCurrentPage('project-detail');
  };

  const handleUpdateProject = async (updatedProject: Project) => {
    try {
      await updateProjectMutation({
        variables: {
          projectId: parseInt(updatedProject.id),
          input: {
            name: updatedProject.name,
            patternText: updatedProject.pattern,
            difficultyLevel: updatedProject.difficulty,
            notes: updatedProject.description,
            isCompleted: updatedProject.status === 'completed',
          }
        }
      });
      await fetchProjects();
      setSelectedProject(updatedProject);
    } catch (error) {
      console.error('Error updating project:', error);
      alert('Failed to update project. Please try again.');
    }
  };

  const handleSavePattern = async (patternData: Partial<SavedPattern> & { patternName?: string; patternNotation?: string; patternInstructions?: string; difficultyLevel?: string }) => {
    try {
      // Check if it's a Pattern object (from manual creation) or pattern data (from YouTube)
      if (patternData.id && patternData.notation) {
        // Already a Pattern object from manual creation - create it in backend
        const fullPattern = patternData as SavedPattern;
        await createProjectMutation({
          variables: {
            input: {
              name: fullPattern.name,
              patternText: fullPattern.notation,
              translatedText: fullPattern.instructions,
              difficultyLevel: fullPattern.difficulty,
              estimatedTime: fullPattern.estimatedTime,
              yarnWeight: fullPattern.materials,
              imageData: fullPattern.images && fullPattern.images.length > 0 ? JSON.stringify(fullPattern.images) : null,
              notes: null, // Patterns have no notes
            }
          }
        });
        await fetchProjects();
        return;
      }

      // YouTube pattern data - transform and save to backend
      const difficultyValue = patternData.difficultyLevel;
      const validDifficulty = difficultyValue === 'beginner' || difficultyValue === 'intermediate' || difficultyValue === 'advanced' 
        ? difficultyValue 
        : 'beginner';

      await createProjectMutation({
        variables: {
          input: {
            name: patternData.patternName || 'Untitled Pattern',
            patternText: patternData.patternNotation || '',
            translatedText: patternData.patternInstructions || '',
            difficultyLevel: validDifficulty,
            estimatedTime: patternData.estimatedTime || '',
            yarnWeight: patternData.materials || '',
            imageData: patternData.thumbnailUrl ? JSON.stringify([patternData.thumbnailUrl]) : null,
            notes: null, // Patterns have no notes
          }
        }
      });
      
      await fetchProjects();
      setCurrentPage('patterns');
    } catch (error) {
      console.error('Error saving pattern:', error);
      alert('Failed to save pattern. Please try again.');
    }
  };

  const handleDeletePattern = async (patternId: string) => {
    try {
      await deleteProjectMutation({
        variables: { projectId: parseInt(patternId) }
      });
      await fetchProjects();
    } catch (error) {
      console.error('Error deleting pattern:', error);
      alert('Failed to delete pattern. Please try again.');
    }
  };

  const handleUpdatePattern = async (updatedPattern: SavedPattern) => {
    try {
      await updateProjectMutation({
        variables: {
          projectId: parseInt(updatedPattern.id),
          input: {
            name: updatedPattern.name,
            patternText: updatedPattern.notation,
            translatedText: updatedPattern.instructions,
            difficultyLevel: updatedPattern.difficulty,
            estimatedTime: updatedPattern.estimatedTime,
            yarnWeight: updatedPattern.materials,
            imageData: updatedPattern.images && updatedPattern.images.length > 0 ? JSON.stringify(updatedPattern.images) : null,
          }
        }
      });
      await fetchProjects();
    } catch (error) {
      console.error('Error updating pattern:', error);
      alert('Failed to update pattern. Please try again.');
    }
  };

  const handleBackToProjects = () => {
    setSelectedProject(null);
    setCurrentPage('projects');
  };

  const handleAuthSuccess = (token: string, userData: { id: string; username: string; email: string }) => {
    setAuthToken(token);
    setUser(userData);
    setShowAuthModal(false);
    // Refresh data after authentication
    fetchProjects();
  };

  const handleLogout = () => {
    localStorage.removeItem('crooked-finger-token');
    localStorage.removeItem('crooked-finger-user');
    setAuthToken(null);
    setUser(null);
    
    setCurrentPage('home');
  };

  const renderCurrentPage = () => {
    const activeConversation = conversations.find(c => c.id === activeConversationId);

    switch (currentPage) {
      case 'home':
        return (
          <HomePage
            recentProjects={projects.slice(0, 3)}
            recentConversations={conversations.slice(0, 3)}
            onNavigate={setCurrentPage}
            onProjectClick={handleProjectClick}
            onConversationClick={handleOpenConversation}
            onNewChat={handleCreateNewChat}
          />
        );
      case 'chat':
        return (
          <div className="flex h-full">
            <ConversationList
              conversations={conversations}
              activeConversationId={activeConversationId}
              onConversationSelect={handleOpenConversation}
              onNewConversation={handleCreateNewChat}
              onDeleteConversation={(id) => {
                setConversations(prev => prev.filter(c => c.id !== id));
                if (activeConversationId === id) {
                  setActiveConversationId(conversations[0]?.id || null);
                }
              }}
            />
            <div className="flex-1">
              <ChatInterface
                chatHistory={activeConversation?.messages || []}
                onSendMessage={handleSendMessage}
                loading={chatLoading}
                onNewChat={handleCreateNewChat}
              />
            </div>
          </div>
        );
      case 'projects':
        return (
          <ProjectsPage
            projects={projects}
            onCreateProject={handleCreateProject}
            onProjectClick={handleProjectClick}
          />
        );
      case 'project-detail':
        return selectedProject ? (
          <ProjectDetailPage
            project={selectedProject}
            onBack={handleBackToProjects}
            onUpdateProject={handleUpdateProject}
          />
        ) : (
          <ProjectsPage
            projects={projects}
            onCreateProject={handleCreateProject}
            onProjectClick={handleProjectClick}
          />
        );
      case 'patterns':
        return (
          <PatternLibrary
            savedPatterns={savedPatterns}
            onSavePattern={handleSavePattern}
            onDeletePattern={handleDeletePattern}
            onUpdatePattern={handleUpdatePattern}
          />
        );
      case 'youtube-test':
        return <YouTubeTest onNavigate={setCurrentPage} onSavePattern={handleSavePattern} />;
      case 'usage':
        return (
          <div className="h-full overflow-auto p-6">
            <AIUsageDashboardComponent />
          </div>
        );
      case 'settings':
        return (
          <div className="h-full overflow-auto p-6">
            <div className="max-w-3xl mx-auto space-y-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">Settings</h1>
                <p className="text-muted-foreground">Customize your Crooked Finger experience</p>
              </div>
              <AIModelSelector />
            </div>
          </div>
        );
      default:
        return (
          <HomePage
            recentProjects={projects.slice(0, 3)}
            recentConversations={conversations.slice(0, 3)}
            onNavigate={setCurrentPage}
            onProjectClick={handleProjectClick}
            onConversationClick={handleOpenConversation}
            onNewChat={handleCreateNewChat}
          />
        );
    }
  };

  return (
    <div className="h-screen bg-gradient-to-br from-background via-background to-card flex">
      <Navigation
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        user={user}
        onLoginClick={() => setShowAuthModal(true)}
        onLogoutClick={handleLogout}
      />
      <main className="flex-1 overflow-hidden">
        {renderCurrentPage()}
      </main>
      {showAuthModal && (
        <AuthModal
          onClose={() => setShowAuthModal(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      )}
    </div>
  );
}
