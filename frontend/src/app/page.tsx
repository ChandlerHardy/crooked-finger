'use client';

import { useState, useEffect } from 'react';
// import { useMutation } from '@apollo/client/react/index.js';
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

  // Load saved patterns from localStorage on mount
  useEffect(() => {
    const loadSavedPatterns = () => {
      try {
        const stored = localStorage.getItem('crooked-finger-patterns');
        if (stored) {
          const parsed = JSON.parse(stored) as SavedPattern[];
          // Convert date strings back to Date objects
          const patternsWithDates = parsed.map((p) => ({
            ...p,
            createdAt: p.createdAt ? new Date(p.createdAt) : new Date(),
          }));
          setSavedPatterns(patternsWithDates);
        }
      } catch (error) {
        console.error('Error loading saved patterns:', error);
      }
    };
    loadSavedPatterns();
  }, []);

  // Save patterns to localStorage whenever they change
  useEffect(() => {
    if (savedPatterns.length > 0) {
      try {
        localStorage.setItem('crooked-finger-patterns', JSON.stringify(savedPatterns));
      } catch (error) {
        console.error('Error saving patterns:', error);
      }
    }
  }, [savedPatterns]);
  // const [chatWithAssistant, { loading: chatLoading }] = useMutation<
  //   ChatWithAssistantResponse,
  //   ChatWithAssistantVariables
  // >(CHAT_WITH_ASSISTANT);

  // Mock data for demonstration
  // Load conversations from localStorage on mount
  useEffect(() => {
    const loadConversations = () => {
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
    loadConversations();
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    if (conversations.length > 0) {
      try {
        localStorage.setItem('crooked-finger-conversations', JSON.stringify(conversations));
      } catch (error) {
        console.error('Error saving conversations:', error);
      }
    }
  }, [conversations]);

  const [projects, setProjects] = useState<Project[]>([
    {
      id: '1',
      name: 'Cozy Blanket',
      description: 'A warm granny square blanket for winter evenings',
      pattern: `CLASSIC GRANNY SQUARE BLANKET

Materials:
- Medium weight yarn (4) in 4 colors
- Size H/8 (5.0mm) crochet hook
- Tapestry needle for joining

GRANNY SQUARE (Make 48):

Round 1: Ch 4, join with sl st to form ring.
Ch 3 (counts as 1st dc), 2 dc in ring, ch 2, *3 dc in ring, ch 2*, repeat from * 2 more times. Join with sl st to top of ch-3. (12 dc, 4 ch-2 spaces)

Round 2: Sl st to first ch-2 space, ch 3, (2 dc, ch 2, 3 dc) in same space (corner made), ch 1, *(3 dc, ch 2, 3 dc) in next ch-2 space, ch 1*, repeat from * 2 more times. Join with sl st to top of ch-3.

Round 3: Sl st to first ch-2 space, ch 3, (2 dc, ch 2, 3 dc) in same space, ch 1, 3 dc in next ch-1 space, ch 1, *(3 dc, ch 2, 3 dc) in next ch-2 space, ch 1, 3 dc in next ch-1 space, ch 1*, repeat from * 2 more times. Join with sl st to top of ch-3.

Continue in this manner until square measures 4 inches.

ASSEMBLY:
Arrange squares in an 8x6 grid.
Join squares using single crochet seams.

BORDER:
Round 1: Work sc around entire blanket edge.
Round 2: Ch 1, sc in each sc around.
Round 3: Repeat Round 2.

Fasten off and weave in ends.`,
      status: 'in-progress',
      difficulty: 'beginner',
      tags: ['blanket', 'granny-square', 'winter'],
      createdAt: new Date('2024-01-15'),
      updatedAt: new Date('2024-01-20'),
      isFavorite: true,
    },
    {
      id: '2',
      name: 'Baby Booties',
      description: 'Adorable booties for newborns',
      pattern: `BABY BOOTIES PATTERN

Size: 0-3 months

Materials:
- Light weight yarn (3) in baby colors
- Size F/5 (3.75mm) crochet hook
- Tapestry needle
- Small buttons (optional)

SOLE:
Ch 15.
Row 1: Sc in 2nd ch from hook, sc in next 12 ch, 3 sc in last ch. Working on opposite side of foundation ch, sc in next 12 ch, 2 sc in last ch. (30 sc)
Row 2: Ch 1, turn. 2 sc in first sc, sc in next 12 sc, 2 sc in next 3 sc, sc in next 12 sc, 2 sc in last 2 sc. (36 sc)

SIDES:
Row 3: Ch 1, turn. Sc in each sc around. (36 sc)
Rows 4-8: Repeat Row 3.

TOE SHAPING:
Row 9: Ch 1, turn. Sc in first 11 sc, [sc2tog] 7 times, sc in last 11 sc. (29 sc)
Row 10: Ch 1, turn. Sc in first 11 sc, [sc2tog] 3 times, sc in last 12 sc. (26 sc)

ANKLE:
Rows 11-14: Ch 1, turn. Sc in each sc around.

STRAP (optional):
Ch 20, sl st to opposite side of bootie.

Make 2.`,
      status: 'completed',
      difficulty: 'intermediate',
      tags: ['baby', 'booties', 'gift'],
      createdAt: new Date('2024-01-10'),
      updatedAt: new Date('2024-01-18'),
      isFavorite: false,
    },
    {
      id: '3',
      name: 'Cable Scarf',
      description: 'Elegant cable pattern scarf',
      pattern: 'FPtr around next 2 sts...',
      status: 'planning',
      difficulty: 'advanced',
      tags: ['scarf', 'cable', 'texture'],
      createdAt: new Date('2024-01-22'),
      updatedAt: new Date('2024-01-22'),
      isFavorite: true,
    },
  ]);

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

  const handleCreateProject = () => {
    // In a real app, this would open a create project modal/form
    console.log('Create new project');
  };

  const handleProjectClick = (project: Project) => {
    setSelectedProject(project);
    setCurrentPage('project-detail');
  };

  const handleUpdateProject = (updatedProject: Project) => {
    setProjects(prevProjects =>
      prevProjects.map(p => p.id === updatedProject.id ? updatedProject : p)
    );
    setSelectedProject(updatedProject);
  };

  const handleSavePattern = (patternData: Partial<SavedPattern> & { patternName?: string; patternNotation?: string; patternInstructions?: string; difficultyLevel?: string }) => {
    // Check if it's a Pattern object (from manual creation) or pattern data (from YouTube)
    if (patternData.id && patternData.notation) {
      // Already a Pattern object from manual creation - cast it properly
      const fullPattern = patternData as SavedPattern;
      setSavedPatterns(prev => [fullPattern, ...prev]);
      return;
    }

    // YouTube pattern data - transform it
    const difficultyValue = patternData.difficultyLevel;
    const validDifficulty: 'beginner' | 'intermediate' | 'advanced' = 
      (difficultyValue === 'beginner' || difficultyValue === 'intermediate' || difficultyValue === 'advanced') 
        ? difficultyValue 
        : 'beginner';

    const newPattern: SavedPattern = {
      id: Date.now().toString(),
      name: patternData.patternName || 'Untitled Pattern',
      description: patternData.description || '',
      difficulty: validDifficulty,
      category: 'youtube-import',
      tags: patternData.videoId ? ['youtube', 'imported'] : ['imported'],
      notation: patternData.patternNotation || '',
      instructions: patternData.patternInstructions || '',
      materials: patternData.materials || '',
      estimatedTime: patternData.estimatedTime || '',
      videoId: patternData.videoId,
      thumbnailUrl: patternData.thumbnailUrl, // YouTube thumbnail will be used as pattern thumbnail
      images: patternData.thumbnailUrl ? [patternData.thumbnailUrl] : [], // Also add to gallery
      isFavorite: false,
      views: 0,
      downloads: 0,
      createdAt: new Date(),
    };
    setSavedPatterns(prev => [newPattern, ...prev]);
    setCurrentPage('patterns');
  };

  const handleDeletePattern = (patternId: string) => {
    setSavedPatterns(prev => prev.filter(p => p.id !== patternId));
  };

  const handleUpdatePattern = (updatedPattern: SavedPattern) => {
    setSavedPatterns(prev =>
      prev.map(p => p.id === updatedPattern.id ? updatedPattern : p)
    );
  };

  const handleBackToProjects = () => {
    setSelectedProject(null);
    setCurrentPage('projects');
  };

  const handleAuthSuccess = (token: string, userData: { id: string; username: string; email: string }) => {
    setAuthToken(token);
    setUser(userData);
    setShowAuthModal(false);
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
