import { gql } from '@apollo/client';

export const GET_PROJECTS = gql`
  query GetProjects {
    projects {
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
      imageData
      userId
      createdAt
      updatedAt
    }
  }
`;

export const GET_PROJECT = gql`
  query GetProject($projectId: Int!) {
    project(projectId: $projectId) {
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
      imageData
      userId
      createdAt
      updatedAt
    }
  }
`;

export const GET_CHAT_MESSAGES = gql`
  query GetChatMessages($projectId: Int, $limit: Int) {
    chatMessages(projectId: $projectId, limit: $limit) {
      id
      message
      response
      messageType
      projectId
      userId
      createdAt
    }
  }
`;

export const GET_CONVERSATIONS = gql`
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
`;

export const GET_CHAT_MESSAGES_BY_CONVERSATION = gql`
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
`;

export const HELLO_QUERY = gql`
  query Hello {
    hello
  }
`;
