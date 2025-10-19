'use client';

import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Sparkles, Check, Settings2, ChevronUp, ChevronDown } from 'lucide-react';
import { apolloClient } from '@/lib/apollo-client';
import { SET_AI_MODEL } from '@/lib/graphql/mutations';

interface AIModelConfig {
  useSmartRouting: boolean;
  primaryModel: string;
  fallbackOrder: string[];
}

interface AIModelSelectorProps {
  onConfigChange?: (config: AIModelConfig) => void;
}

const AVAILABLE_MODELS = [
  { id: 'openrouter-qwen', name: 'OpenRouter Qwen3-30B', provider: 'OpenRouter', free: true },
  { id: 'openrouter-deepseek', name: 'OpenRouter DeepSeek V3.1', provider: 'OpenRouter', free: true },
  { id: 'gemini-pro', name: 'Gemini 2.5 Pro', provider: 'Google', quota: '100/day' },
  { id: 'gemini-flash-preview', name: 'Gemini 2.5 Flash Preview', provider: 'Google', quota: '250/day' },
  { id: 'gemini-flash', name: 'Gemini 2.5 Flash', provider: 'Google', quota: '250/day' },
  { id: 'gemini-flash-lite', name: 'Gemini 2.5 Flash-Lite', provider: 'Google', quota: '1000/day' },
];

// Map frontend model IDs to backend model names
const MODEL_ID_TO_BACKEND_NAME: Record<string, string> = {
  'openrouter-qwen': 'qwen/qwen3-30b-a3b:free',
  'openrouter-deepseek': 'deepseek/deepseek-chat-v3.1:free',
  'gemini-pro': 'gemini-2.5-pro',
  'gemini-flash-preview': 'gemini-2.5-flash-preview-09-2025',
  'gemini-flash': 'gemini-2.5-flash',
  'gemini-flash-lite': 'gemini-2.5-flash-lite',
};

export function AIModelSelector({ onConfigChange }: AIModelSelectorProps) {
  const [config, setConfig] = useState<AIModelConfig>({
    useSmartRouting: false,
    primaryModel: 'gemini-flash',
    fallbackOrder: ['gemini-flash', 'gemini-flash-preview', 'openrouter-deepseek', 'gemini-pro', 'gemini-flash-lite', 'openrouter-qwen'],
  });

  // Load saved config from localStorage and sync with backend
  useEffect(() => {
    const loadAndSyncConfig = async () => {
      try {
        const saved = localStorage.getItem('crooked-finger-ai-config');
        if (saved) {
          const parsed = JSON.parse(saved) as AIModelConfig;
          setConfig(parsed);

          // Sync the loaded config with backend
          try {
            if (parsed.useSmartRouting) {
              await apolloClient.mutate({
                mutation: SET_AI_MODEL,
                variables: {
                  modelName: null,
                  priorityOrder: parsed.fallbackOrder.map(id => MODEL_ID_TO_BACKEND_NAME[id]),
                },
              });
            } else {
              const backendModelName = MODEL_ID_TO_BACKEND_NAME[parsed.primaryModel];
              await apolloClient.mutate({
                mutation: SET_AI_MODEL,
                variables: {
                  modelName: backendModelName,
                  priorityOrder: parsed.fallbackOrder.map(id => MODEL_ID_TO_BACKEND_NAME[id]),
                },
              });
            }
          } catch (error) {
            console.error('Error syncing initial AI config with backend:', error);
          }
        }
      } catch (error) {
        console.error('Error loading AI config:', error);
      }
    };

    loadAndSyncConfig();
  }, []);

  // Save config to localStorage, notify parent, and sync with backend
  const updateConfig = async (updates: Partial<AIModelConfig>) => {
    let newConfig = { ...config, ...updates };

    // If primary model changed, ensure it's at the top of fallback order
    if (updates.primaryModel && updates.primaryModel !== config.primaryModel) {
      const newFallbackOrder = [
        updates.primaryModel,
        ...config.fallbackOrder.filter(id => id !== updates.primaryModel)
      ];
      newConfig = { ...newConfig, fallbackOrder: newFallbackOrder };
    }

    setConfig(newConfig);
    localStorage.setItem('crooked-finger-ai-config', JSON.stringify(newConfig));
    onConfigChange?.(newConfig);

    // Sync with backend
    try {
      if (newConfig.useSmartRouting) {
        // Smart routing: pass null for model_name to enable complexity-based routing
        await apolloClient.mutate({
          mutation: SET_AI_MODEL,
          variables: {
            modelName: null,
            priorityOrder: newConfig.fallbackOrder.map(id => MODEL_ID_TO_BACKEND_NAME[id]),
          },
        });
      } else {
        // Single model or fallback chain
        const backendModelName = MODEL_ID_TO_BACKEND_NAME[newConfig.primaryModel];
        await apolloClient.mutate({
          mutation: SET_AI_MODEL,
          variables: {
            modelName: backendModelName,
            priorityOrder: newConfig.fallbackOrder.map(id => MODEL_ID_TO_BACKEND_NAME[id]),
          },
        });
      }
    } catch (error) {
      console.error('Error syncing AI config with backend:', error);
    }
  };

  // Move model up in fallback order
  const moveModelUp = (index: number) => {
    if (index === 0) return; // Already at top
    const newOrder = [...config.fallbackOrder];
    [newOrder[index - 1], newOrder[index]] = [newOrder[index], newOrder[index - 1]];
    updateConfig({ fallbackOrder: newOrder });
  };

  // Move model down in fallback order
  const moveModelDown = (index: number) => {
    if (index === config.fallbackOrder.length - 1) return; // Already at bottom
    const newOrder = [...config.fallbackOrder];
    [newOrder[index], newOrder[index + 1]] = [newOrder[index + 1], newOrder[index]];
    updateConfig({ fallbackOrder: newOrder });
  };

  return (
    <Card className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
          <Sparkles className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h3 className="text-lg font-semibold">AI Model Settings</h3>
          <p className="text-sm text-muted-foreground">Configure which AI models to use</p>
        </div>
      </div>

      {/* Smart Routing Toggle */}
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
          <div className="space-y-0.5">
            <Label htmlFor="smart-routing" className="text-base">Smart Routing</Label>
            <p className="text-sm text-muted-foreground">
              Automatically select the best model based on query complexity
            </p>
          </div>
          <Switch
            id="smart-routing"
            checked={config.useSmartRouting}
            onCheckedChange={(checked) => updateConfig({ useSmartRouting: checked })}
          />
        </div>

      </div>

      {/* Primary Model Selection */}
      {!config.useSmartRouting && (
        <div className="space-y-3">
          <Label htmlFor="primary-model">Primary Model</Label>
          <Select
            value={config.primaryModel}
            onValueChange={(value) => updateConfig({ primaryModel: value })}
          >
            <SelectTrigger id="primary-model">
              <SelectValue placeholder="Select primary model" />
            </SelectTrigger>
            <SelectContent>
              {AVAILABLE_MODELS.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  <div className="flex items-center gap-2">
                    <span>{model.name}</span>
                    {model.free && (
                      <span className="text-xs bg-green-500/10 text-green-600 px-2 py-0.5 rounded-full">
                        Free
                      </span>
                    )}
                    {model.quota && (
                      <span className="text-xs bg-blue-500/10 text-blue-600 px-2 py-0.5 rounded-full">
                        {model.quota}
                      </span>
                    )}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Fallback Order */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Settings2 className="h-4 w-4 text-muted-foreground" />
            <Label>Fallback Order</Label>
          </div>
          <p className="text-xs text-muted-foreground">Click arrows to reorder</p>
        </div>
        <div className="space-y-2">
          {config.fallbackOrder.map((modelId, index) => {
            const model = AVAILABLE_MODELS.find((m) => m.id === modelId);
            if (!model) return null;

            return (
              <div
                key={modelId}
                className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg"
              >
                <div className="w-6 h-6 bg-primary/20 rounded-full flex items-center justify-center text-xs font-medium">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{model.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {model.provider} {model.quota && `• ${model.quota}`}
                    {model.free && ' • Free & Unlimited'}
                  </p>
                </div>
                {config.primaryModel === modelId && (
                  <div className="flex items-center gap-1 text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                    <Check className="h-3 w-3" />
                    Primary
                  </div>
                )}
                <div className="flex flex-col gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={() => moveModelUp(index)}
                    disabled={index === 0}
                  >
                    <ChevronUp className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={() => moveModelDown(index)}
                    disabled={index === config.fallbackOrder.length - 1}
                  >
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <p className="text-sm text-blue-600 dark:text-blue-400">
          <strong>How it works:</strong> The primary model handles all requests. If it fails or reaches quota limits,
          the system automatically falls back to the next available model in the fallback order.
        </p>
      </div>
    </Card>
  );
}
