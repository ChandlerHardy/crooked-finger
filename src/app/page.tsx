'use client';

import { useState } from 'react';
// import { useMutation } from '@apollo/client/react/index.js';
import { Navigation } from '../components/Navigation';
import { HomePage } from '../components/HomePage';
import { ChatInterface } from '../components/ChatInterface';
import { ProjectsPage } from '../components/ProjectsPage';
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
  const [chatLoading, setChatLoading] = useState(false);
  // const [chatWithAssistant, { loading: chatLoading }] = useMutation<
  //   ChatWithAssistantResponse,
  //   ChatWithAssistantVariables
  // >(CHAT_WITH_ASSISTANT);

  // Mock data for demonstration
  const [projects] = useState<Project[]>([
    {
      id: '1',
      name: 'Cozy Blanket',
      description: 'A warm granny square blanket for winter evenings',
      pattern: 'Ch 4, join with sl st to form ring...',
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
      pattern: 'Foundation: Ch 15...',
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
    // In a real app, this would navigate to project details
    console.log('Project clicked:', project.name);
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
