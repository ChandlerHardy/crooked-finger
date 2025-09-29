'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@apollo/client/react';
import { gql } from '@apollo/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Zap, Activity, TrendingUp, Gauge, Clock } from 'lucide-react';
import { AIUsageDashboard as AIUsageDashboardType, GetAIUsageDashboardResponse } from '@/types/graphql';

const GET_AI_USAGE_DASHBOARD = gql`
  query GetAIUsageDashboard {
    aiUsageDashboard {
      totalRequestsToday
      totalRemaining
      models {
        modelName
        currentUsage
        dailyLimit
        remaining
        percentageUsed
        priority
        useCase
      }
    }
  }
`;

const getPriorityColor = (priority: number) => {
  switch (priority) {
    case 1: return 'bg-purple-500';
    case 2: return 'bg-blue-500';
    case 3: return 'bg-green-500';
    case 4: return 'bg-yellow-500';
    default: return 'bg-gray-500';
  }
};

const getPriorityLabel = (priority: number) => {
  switch (priority) {
    case 1: return 'Premium';
    case 2: return 'Fast';
    case 3: return 'Standard';
    case 4: return 'Efficient';
    default: return 'Unknown';
  }
};

const getUsageColor = (percentage: number) => {
  if (percentage >= 90) return 'text-red-600 dark:text-red-400';
  if (percentage >= 70) return 'text-yellow-600 dark:text-yellow-400';
  if (percentage >= 50) return 'text-blue-600 dark:text-blue-400';
  return 'text-green-600 dark:text-green-400';
};

const formatModelName = (modelName: string) => {
  return modelName
    .replace('gemini-', '')
    .replace('-', ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export default function AIUsageDashboardComponent() {
  const [timeUntilReset, setTimeUntilReset] = useState('');

  const { data, loading, error, refetch } = useQuery<GetAIUsageDashboardResponse>(
    GET_AI_USAGE_DASHBOARD,
    {
      pollInterval: 30000, // Refresh every 30 seconds
      errorPolicy: 'all'
    }
  );

  // Calculate time until quota reset (midnight PST)
  useEffect(() => {
    const updateCountdown = () => {
      const now = new Date();

      // Create midnight PST for today
      const pstOffset = -8; // PST is UTC-8 (during standard time)
      const pdtOffset = -7; // PDT is UTC-7 (during daylight time)

      // Determine if we're in daylight saving time (approximate)
      const isDST = now.getMonth() >= 2 && now.getMonth() <= 10; // March-November roughly
      const timezoneOffset = isDST ? pdtOffset : pstOffset;

      // Get next midnight PST/PDT
      const nextMidnightPST = new Date();
      nextMidnightPST.setUTCDate(now.getUTCDate() + 1);
      nextMidnightPST.setUTCHours(-timezoneOffset, 0, 0, 0); // Convert PST/PDT to UTC

      const timeDiff = nextMidnightPST.getTime() - now.getTime();

      if (timeDiff > 0) {
        const hours = Math.floor(timeDiff / (1000 * 60 * 60));
        const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

        setTimeUntilReset(`${hours}h ${minutes}m ${seconds}s`);
      } else {
        setTimeUntilReset('Resetting now...');
      }
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            AI Usage Dashboard
          </CardTitle>
          <CardDescription>Loading usage statistics...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full border-red-200 dark:border-red-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600 dark:text-red-400">
            <Activity className="h-5 w-5" />
            AI Usage Dashboard - Error
          </CardTitle>
          <CardDescription>Failed to load usage statistics</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {error.message}
          </p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Retry
          </button>
        </CardContent>
      </Card>
    );
  }

  const dashboard: AIUsageDashboardType | undefined = data?.aiUsageDashboard;
  if (!dashboard) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            AI Usage Dashboard
          </CardTitle>
          <CardDescription>No usage data available</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const sortedModels = [...dashboard.models].sort((a, b) => a.priority - b.priority);

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              AI Usage Dashboard
            </CardTitle>
            <CardDescription>
              Daily quota tracking for Gemini models
            </CardDescription>
          </div>
          <button
            onClick={() => refetch()}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            title="Refresh usage data"
          >
            <TrendingUp className="h-4 w-4" />
          </button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="h-4 w-4 text-green-600 dark:text-green-400" />
              <span className="font-semibold text-green-700 dark:text-green-300">
                Total Requests Today
              </span>
            </div>
            <p className="text-2xl font-bold text-green-900 dark:text-green-100">
              {dashboard.totalRequestsToday}
            </p>
          </div>

          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-2 mb-2">
              <Gauge className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span className="font-semibold text-blue-700 dark:text-blue-300">
                Total Remaining
              </span>
            </div>
            <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
              {dashboard.totalRemaining}
            </p>
          </div>
        </div>

        <Separator />

        {/* Quota Reset Information */}
        <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-orange-600 dark:text-orange-400" />
            <span className="font-semibold text-orange-700 dark:text-orange-300">
              Quota Reset Timer
            </span>
          </div>
          <p className="text-sm text-orange-600 dark:text-orange-400 mb-2">
            All model quotas reset at midnight PST/PDT (Pacific Time)
          </p>
          <div className="text-lg font-mono font-bold text-orange-900 dark:text-orange-100">
            Next reset in: {timeUntilReset}
          </div>
        </div>

        <Separator />

        {/* Model-specific Usage */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold mb-4">Model Usage Breakdown</h3>

          {sortedModels.map((model) => (
            <div
              key={model.modelName}
              className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <h4 className="font-semibold">{formatModelName(model.modelName)}</h4>
                  <Badge
                    variant="secondary"
                    className={`${getPriorityColor(model.priority)} text-white`}
                  >
                    {getPriorityLabel(model.priority)}
                  </Badge>
                  <Badge variant="outline">
                    {model.useCase.replace('_', ' ')}
                  </Badge>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-medium ${getUsageColor(model.percentageUsed)}`}>
                    {model.percentageUsed}% used
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {model.currentUsage} / {model.dailyLimit}
                  </p>
                </div>
              </div>

              <Progress
                value={model.percentageUsed}
                className="h-2"
                indicatorClassName={
                  model.percentageUsed >= 90
                    ? 'bg-red-500'
                    : model.percentageUsed >= 70
                    ? 'bg-yellow-500'
                    : 'bg-green-500'
                }
              />

              <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
                <span>Remaining: {model.remaining} requests</span>
                <span>
                  Status: {
                    model.percentageUsed >= 100
                      ? 'Quota Exhausted'
                      : model.percentageUsed >= 90
                      ? 'Almost Full'
                      : 'Available'
                  }
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Smart Routing Info */}
        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <h4 className="font-semibold mb-2">Smart Routing Active</h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            The AI service automatically selects the best available model based on request complexity and quota availability.
            Complex tasks use higher-tier models, while simple queries conserve premium quota.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}