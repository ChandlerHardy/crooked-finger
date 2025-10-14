import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

const httpLink = createHttpLink({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'https://backend.chandlerhardy.com/crooked-finger/graphql',
});

export const apolloClient = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
    },
    query: {
      errorPolicy: 'all',
    },
  },
});

import { DocumentNode } from 'graphql';

// Simple function to create query with auth
export const fetchWithAuth = async (query: string | DocumentNode, variables?: Record<string, unknown>) => {
  // Only run fetchWithAuth on client-side
  if (typeof window === 'undefined') {
    return { data: null, errors: [{ message: 'Server-side rendering - not available' }] };
  }
  
  const token = localStorage.getItem('crooked-finger-token');
  console.log('🔐 Auth token present:', !!token);
  
  // Convert DocumentNode to string if needed
  const queryString = typeof query === 'string' ? query : (query as DocumentNode).loc?.source.body || '';
  
  const response = await fetch(process.env.NEXT_PUBLIC_GRAPHQL_URL || 'https://backend.chandlerhardy.com/crooked-finger/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ query: queryString, variables }),
  });
  
  const result = await response.json();
  console.log('📥 GraphQL response:', result);
  return result;
};