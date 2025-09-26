'use client';

import { useState } from 'react';
import { Navigation } from '../components/Navigation';
import { HomePage } from '../components/HomePage';
import { ChatInterface } from '../components/ChatInterface';
import { ProjectsPage } from '../components/ProjectsPage';
import { PatternLibrary } from '../components/PatternLibrary';

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
}

export default function Home() {
  const [currentPage, setCurrentPage] = useState('home');

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

  const handleSendMessage = (message: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      isPattern: message.includes('ch ') || message.includes('dc') || message.includes('sc') || message.includes('tog'),
    };

    setChatHistory(prev => [...prev, userMessage]);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: generateAIResponse(message),
        timestamp: new Date(),
        isPattern: true,
      };
      setChatHistory(prev => [...prev, assistantMessage]);
    }, 1000);
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
