'use client';

import { useState, useEffect, useCallback } from 'react';
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
import { GET_PROJECTS } from '../lib/graphql/queries';
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
  backendId?: number | null; // Backend conversation ID for sync between platforms
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
  const [conversationLoading, setConversationLoading] = useState(false);
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
        .map((project: any) => {
          const images = project.imageData ? JSON.parse(project.imageData) : [];
          console.log('🖼️ Pattern images loaded:', {
            projectId: project.id,
            projectName: project.name,
            imageCount: images.length,
            firstImagePreview: images[0]?.substring(0, 50) + '...',
          });
          return {
            id: project.id.toString(),
            name: project.name,
            description: undefined, // Don't show instructions as description
            difficulty: project.difficultyLevel as 'beginner' | 'intermediate' | 'advanced',
            category: 'imported',
            tags: [],
            notation: project.patternText || '',
            instructions: project.translatedText || '',
            materials: project.yarnWeight || '',
            estimatedTime: project.estimatedTime || '',
            images,
            thumbnailUrl: images.length > 0 ? images[0] : undefined,
            isFavorite: false,
            views: 0,
            downloads: 0,
            createdAt: new Date(project.createdAt),
          };
        });
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
  
  const loadConversations = useCallback(async () => {
    // Check if we're in browser environment
    if (typeof window === 'undefined') return;
    
    try {
      // First load conversations from backend if user is authenticated
      if (authToken) {
        const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://150.136.38.166:8001/crooked-finger/graphql';
        
        const response = await fetch(graphqlUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`,
          },
          body: JSON.stringify({
            query: `
              query GetConversations($limit: Int) {
                conversations(limit: $limit) {
                  id
                  title
                  userId
                  createdAt
                  updatedAt
                  messageCount
                }
              }
            `,
            variables: {
              limit: 50
            }
          }),
        });

        const result = await response.json();
        
        if (result.data?.conversations) {
          // Define the backend conversation type
          interface BackendConversation {
            id: number;
            title: string;
            userId: number;
            createdAt: string;
            updatedAt: string;
            messageCount: number;
          }

          // Convert backend conversations to app format
          const backendConversations: ChatConversation[] = result.data.conversations.map((conv: BackendConversation) => ({
            id: `backend-${conv.id}`, // Create a unique ID to distinguish from local-only conversations
            title: conv.title,
            messages: [], // We'll load messages when conversation is selected
            createdAt: new Date(conv.createdAt),
            updatedAt: new Date(conv.updatedAt),
            backendId: conv.id, // Store the backend ID for sync
          }));

          // Also load from localStorage as fallback/cache
          let localConversations: ChatConversation[] = [];
          const stored = localStorage.getItem('crooked-finger-conversations');
          if (stored) {
            const parsed = JSON.parse(stored) as ChatConversation[];
            localConversations = parsed.map((conv) => ({
              ...conv,
              createdAt: conv.createdAt ? new Date(conv.createdAt) : new Date(),
              updatedAt: conv.updatedAt ? new Date(conv.updatedAt) : new Date(),
              messages: conv.messages.map((msg) => ({
                ...msg,
                timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
              })),
            }));
          }

          // Combine backend and local conversations, prioritizing backend
          const allConversations = [...backendConversations, ...localConversations.filter(local => 
            !backendConversations.some(backend => backend.backendId === local.backendId)
          )];

          setConversations(allConversations);

          // Set most recent conversation as active
          if (allConversations.length > 0) {
            setActiveConversationId(allConversations[0].id);
          }
        } else {
          // Fallback to localStorage if backend fails
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
        }
      } else {
        // Load from localStorage if not authenticated
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
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
      // Fallback to localStorage if there's an error
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
      } catch (localStorageError) {
        console.error('Error loading conversations from localStorage:', localStorageError);
      }
    }
  }, [authToken, setConversations, setActiveConversationId]); // Dependencies for useCallback
  
  // Load conversations only on client side
  useEffect(() => {
    const loadConversationsAsync = async () => {
      await loadConversations();
    };
    loadConversationsAsync();
  }, [authToken, loadConversations]);

  const [projects, setProjects] = useState<Project[]>([]);

  const handleCreateNewChat = async () => {
    if (authToken) {
      // Create conversation on backend
      const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://150.136.38.166:8001/crooked-finger/graphql';
      
      try {
        const response = await fetch(graphqlUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`,
          },
          body: JSON.stringify({
            query: `
              mutation CreateConversation($input: CreateConversationInput!) {
                createConversation(input: $input) {
                  id
                  title
                  createdAt
                  updatedAt
                }
              }
            `,
            variables: {
              input: {
                title: 'New Chat'
              }
            }
          }),
        });

        const result = await response.json();
        
        if (result.data?.createConversation) {
          const backendConv = result.data.createConversation;
          const newConversation: ChatConversation = {
            id: `backend-${backendConv.id}`, // Create a unique ID
            title: backendConv.title,
            messages: [],
            createdAt: new Date(backendConv.createdAt),
            updatedAt: new Date(backendConv.updatedAt),
            backendId: backendConv.id, // Store the backend ID for sync
          };
          setConversations(prev => [newConversation, ...prev]);
          setActiveConversationId(newConversation.id);
          setCurrentPage('chat');
        } else {
          // Fallback to local conversation if backend fails
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
        }
      } catch (error) {
        console.error('Error creating conversation on backend:', error);
        // Fallback to local conversation if backend fails
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
      }
    } else {
      // Create local conversation if not authenticated
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
    }
  };

  const handleOpenConversation = async (conversationId: string) => {
    // Set active conversation immediately for responsive UI
    setActiveConversationId(conversationId);
    setCurrentPage('chat');

    // If conversation has a backend ID and user is authenticated, load messages from backend
    const conversation = conversations.find(c => c.id === conversationId);

    // Skip loading if messages are already loaded
    if (conversation && conversation.messages.length > 0) {
      return;
    }

    if (conversation?.backendId && authToken) {
      setConversationLoading(true);
      try {
        const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://150.136.38.166:8001/crooked-finger/graphql';

        const response = await fetch(graphqlUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`,
          },
          body: JSON.stringify({
            query: `
              query GetChatMessagesByConversation($conversationId: Int!, $limit: Int) {
                chatMessages(conversationId: $conversationId, limit: $limit) {
                  id
                  message
                  response
                  messageType
                  conversationId
                  projectId
                  userId
                  createdAt
                }
              }
            `,
            variables: {
              conversationId: conversation.backendId,
              limit: 100
            }
          }),
        });

        const result = await response.json();

        if (result.data?.chatMessages) {
          // Define the backend chat message type
          interface BackendChatMessage {
            id: number;
            message: string;
            response: string;
            messageType: string;
            conversationId: number | null;
            projectId: number | null;
            userId: number;
            createdAt: string;
          }

          // Convert backend messages to app format
          const messages: ChatMessage[] = [];
          for (const msg of result.data.chatMessages as BackendChatMessage[]) {
            messages.push({
              id: `backend-${msg.id}-user`,
              type: 'user',
              content: msg.message,
              timestamp: new Date(msg.createdAt),
            });
            messages.push({
              id: `backend-${msg.id}-assistant`,
              type: 'assistant',
              content: msg.response,
              timestamp: new Date(msg.createdAt),
            });
          }

          // Update conversation with loaded messages
          setConversations(prev => prev.map(conv => {
            if (conv.id === conversationId) {
              return {
                ...conv,
                messages: messages,
              };
            }
            return conv;
          }));
        } else if (result.errors) {
          console.error('GraphQL errors loading messages:', result.errors);
        }
      } catch (error) {
        console.error('Error loading messages from backend:', error);
      } finally {
        setConversationLoading(false);
      }
    }
  };

  const handleSendMessage = async (message: string, images?: string[]) => {
    // Create new conversation if none exists or none is active
    const conversationId = activeConversationId;
    let backendConversationId: number | null = null;
    
    // Check if the current conversation has a backend ID
    const activeConv = conversations.find(c => c.id === activeConversationId);
    if (activeConv && activeConv.backendId) {
      backendConversationId = activeConv.backendId;
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      isPattern: message.includes('ch ') || message.includes('dc') || message.includes('sc') || message.includes('tog'),
    };

    // Update conversation with new message first
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

      // Create conversation on backend if needed
      if (!backendConversationId) {
        // Create a new conversation on the backend
        const createConvResponse = await fetch(graphqlUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
          },
          body: JSON.stringify({
            query: `
              mutation CreateConversation($input: CreateConversationInput!) {
                createConversation(input: $input) {
                  id
                  title
                  createdAt
                  updatedAt
                }
              }
            `,
            variables: {
              input: {
                title: message.slice(0, 50) + (message.length > 50 ? '...' : '')
              }
            }
          }),
        });

        const createConvResult = await createConvResponse.json();
        
        if (createConvResult.data?.createConversation) {
          backendConversationId = createConvResult.data.createConversation.id;
          
          // Update our conversation with the backend ID
          setConversations(prev => prev.map(conv => {
            if (conv.id === conversationId && backendConversationId !== null) {
              const updatedConv = {
                ...conv,
                backendId: backendConversationId
              };
              return updatedConv;
            }
            return conv;
          }));
        }
      }

      // Prepare variables with optional image data and conversation ID
      const variables: Record<string, unknown> = {
        message,
        context: 'crochet_pattern_assistant',
      };

      // Add conversation ID if we have one
      if (backendConversationId) {
        variables.conversationId = backendConversationId;
      }

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
            mutation ChatWithAssistantEnhanced($message: String!, $context: String, $imageData: String, $conversationId: Int) {
              chatWithAssistantEnhanced(message: $message, context: $context, imageData: $imageData, conversationId: $conversationId) {
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
            const updatedConv = {
              ...conv,
              messages: [...conv.messages, assistantMessage],
              updatedAt: new Date(),
            };
            return updatedConv;
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
              onDeleteConversation={async (id) => {
                // Try to delete from backend first if it has a backend ID
                const conversationToDelete = conversations.find(c => c.id === id);
                if (conversationToDelete?.backendId && authToken) {
                  try {
                    const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://150.136.38.166:8001/crooked-finger/graphql';
                    
                    await fetch(graphqlUrl, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`,
                      },
                      body: JSON.stringify({
                        query: `
                          mutation DeleteConversation($conversationId: Int!) {
                            deleteConversation(conversationId: $conversationId)
                          }
                        `,
                        variables: {
                          conversationId: conversationToDelete.backendId
                        }
                      }),
                    });
                  } catch (error) {
                    console.error('Error deleting conversation from backend:', error);
                  }
                }
                
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
                conversationLoading={conversationLoading}
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
