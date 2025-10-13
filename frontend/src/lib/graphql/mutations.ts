import { gql } from '@apollo/client';

export const CHAT_WITH_ASSISTANT = gql`
  mutation ChatWithAssistant($message: String!, $context: String) {
    chatWithAssistant(message: $message, context: $context)
  }
`;

export const CREATE_PROJECT = gql`
  mutation CreateProject($input: CreateProjectInput!) {
    createProject(input: $input) {
      id
      name
      patternText
      translatedText
      difficultyLevel
      estimatedTime
      yarnWeight
      hookSize
      notes
      isCompleted
      userId
      createdAt
      updatedAt
    }
  }
`;

export const UPDATE_PROJECT = gql`
  mutation UpdateProject($projectId: Int!, $input: UpdateProjectInput!) {
    updateProject(projectId: $projectId, input: $input) {
      id
      name
      patternText
      translatedText
      difficultyLevel
      estimatedTime
      yarnWeight
      hookSize
      notes
      isCompleted
      userId
      createdAt
      updatedAt
    }
  }
`;

export const DELETE_PROJECT = gql`
  mutation DeleteProject($projectId: Int!) {
    deleteProject(projectId: $projectId)
  }
`;

export const SET_AI_MODEL = gql`
  mutation SetAiModel($modelName: String, $priorityOrder: [String!]) {
    setAiModel(modelName: $modelName, priorityOrder: $priorityOrder) {
      useOpenrouter
      currentProvider
      selectedModel
      availableModels
      modelPriorityOrder
    }
  }
`;
