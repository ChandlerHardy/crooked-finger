'use client';

import { useState } from 'react';
// import { useMutation } from '@apollo/client/react/index.js';
import { Navigation } from '../components/Navigation';
import { HomePage } from '../components/HomePage';
import { ChatInterface } from '../components/ChatInterface';
import { ProjectsPage } from '../components/ProjectsPage';
import { ProjectDetailPage } from '../components/ProjectDetailPage';
import { PatternLibrary } from '../components/PatternLibrary';
import AIUsageDashboardComponent from '../components/AIUsageDashboard';
import { CHAT_WITH_ASSISTANT } from '../lib/graphql/mutations';
import { ChatWithAssistantVariables, ChatWithAssistantResponse } from '../types/graphql';

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

export default function Home() {
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [chatLoading, setChatLoading] = useState(false);
  // const [chatWithAssistant, { loading: chatLoading }] = useMutation<
  //   ChatWithAssistantResponse,
  //   ChatWithAssistantVariables
  // >(CHAT_WITH_ASSISTANT);

  // Mock data for demonstration
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

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);

  const handleSendMessage = async (message: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      isPattern: message.includes('ch ') || message.includes('dc') || message.includes('sc') || message.includes('tog'),
    };

    setChatHistory(prev => [...prev, userMessage]);
    setChatLoading(true);

    try {
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
            context: 'crochet_pattern_assistant',
          },
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
        setChatHistory(prev => [...prev, assistantMessage]);
      } else if (result.errors) {
        console.error('GraphQL errors:', result.errors);
        throw new Error('GraphQL mutation not available');
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
      setChatHistory(prev => [...prev, assistantMessage]);
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
    setProjects(prev => prev.map(p => p.id === updatedProject.id ? updatedProject : p));
    setSelectedProject(updatedProject);
  };

  const handleBackToProjects = () => {
    setSelectedProject(null);
    setCurrentPage('projects');
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'home':
        return (
          <HomePage
            recentProjects={projects.slice(0, 3)}
            recentChats={chatHistory.slice(-3)}
            onNavigate={setCurrentPage}
          />
        );
      case 'chat':
        return (
          <ChatInterface
            chatHistory={chatHistory}
            onSendMessage={handleSendMessage}
            loading={chatLoading}
          />
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
        return <PatternLibrary />;
      case 'usage':
        return (
          <div className="h-full overflow-auto p-6">
            <AIUsageDashboardComponent />
          </div>
        );
      case 'settings':
        return (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-medium mb-2">Settings</h2>
              <p className="text-muted-foreground">Settings panel coming soon!</p>
            </div>
          </div>
        );
      default:
        return (
          <HomePage
            recentProjects={projects.slice(0, 3)}
            recentChats={chatHistory.slice(-3)}
            onNavigate={setCurrentPage}
          />
        );
    }
  };

  return (
    <div className="h-screen bg-gradient-to-br from-background via-background to-card flex">
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
      <main className="flex-1 overflow-hidden">
        {renderCurrentPage()}
      </main>
    </div>
  );
}
