export interface Project {
  id: string;
  name: string;
  description: string;
  pattern: string;
  status: 'planning' | 'in-progress' | 'completed';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  createdAt: string;
  updatedAt: string;
  isFavorite: boolean;
}

export interface CreateProjectInput {
  name: string;
  description: string;
  pattern: string;
  status: 'planning' | 'in-progress' | 'completed';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  isFavorite?: boolean;
}

export interface UpdateProjectInput {
  name?: string;
  description?: string;
  pattern?: string;
  status?: 'planning' | 'in-progress' | 'completed';
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  tags?: string[];
  isFavorite?: boolean;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isPattern?: boolean;
}

// GraphQL operation types
export interface ChatWithAssistantVariables {
  message: string;
  context?: string;
}

export interface ChatWithAssistantResponse {
  chatWithAssistant: string;
}

export interface GetProjectsResponse {
  projects: Project[];
}

export interface GetProjectResponse {
  project: Project;
}

export interface CreateProjectResponse {
  createProject: Project;
}

export interface UpdateProjectResponse {
  updateProject: Project;
}

// AI Usage Dashboard types
export interface ModelUsageStats {
  modelName: string;
  currentUsage: number;
  dailyLimit: number;
  remaining: number;
  percentageUsed: number;
  priority: number;
  useCase: string;
  totalInputCharacters: number;
  totalOutputCharacters: number;
  totalInputTokens: number;
  totalOutputTokens: number;
}

export interface AIUsageDashboard {
  totalRequestsToday: number;
  totalRemaining: number;
  models: ModelUsageStats[];
}

export interface GetAIUsageDashboardResponse {
  aiUsageDashboard: AIUsageDashboard;
}