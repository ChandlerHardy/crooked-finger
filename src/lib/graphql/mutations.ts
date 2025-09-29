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
      description
      pattern
      status
      difficulty
      tags
      createdAt
      updatedAt
      isFavorite
    }
  }
`;

export const UPDATE_PROJECT = gql`
  mutation UpdateProject($id: ID!, $input: UpdateProjectInput!) {
    updateProject(id: $id, input: $input) {
      id
      name
      description
      pattern
      status
      difficulty
      tags
      createdAt
      updatedAt
      isFavorite
    }
  }
`;