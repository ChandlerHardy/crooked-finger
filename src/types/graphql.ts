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