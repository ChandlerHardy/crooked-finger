import { gql } from '@apollo/client';

export const GET_PROJECTS = gql`
  query GetProjects {
    projects {
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

export const GET_PROJECT = gql`
  query GetProject($id: ID!) {
    project(id: $id) {
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

export const HELLO_QUERY = gql`
  query Hello {
    hello
  }
`;