'use client';

import { useState } from 'react';
import { AIModelSelector } from './AIModelSelector';
import AIUsageDashboardComponent from './AIUsageDashboard';

interface SettingsPageProps {
  user?: { id: string; username: string; email: string } | null;
  onLogout?: () => void;
}

type SettingsTab = 'models' | 'usage' | 'account';

export function SettingsPage({ user, onLogout }: SettingsPageProps) {
  const [activeTab, setActiveTab] = useState<SettingsTab>('models');

  const tabs = [
    { id: 'models' as SettingsTab, label: 'AI Models', icon: '🤖' },
    { id: 'usage' as SettingsTab, label: 'Usage', icon: '📊' },
    ...(user ? [{ id: 'account' as SettingsTab, label: 'Account', icon: '👤' }] : []),
  ];

  return (
    <div className="h-full overflow-y-scroll p-6">
      <div className="w-full space-y-6">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Settings</h1>
          <p className="text-muted-foreground">Customize your Crooked Finger experience</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-border max-w-3xl mx-auto">
          <div className="flex gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="pt-2 min-h-[400px] max-w-3xl mx-auto">
          {activeTab === 'models' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold mb-1">AI Model Configuration</h2>
                <p className="text-sm text-muted-foreground">Choose which AI models to use for assistance</p>
              </div>
              <AIModelSelector />
            </div>
          )}

          {activeTab === 'usage' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold mb-1">AI Usage Dashboard</h2>
                <p className="text-sm text-muted-foreground">Monitor your AI model usage and quotas</p>
              </div>
              <AIUsageDashboardComponent />
            </div>
          )}

          {activeTab === 'account' && user && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold mb-1">Account Settings</h2>
                <p className="text-sm text-muted-foreground">Manage your account</p>
              </div>
              <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-2xl p-4 border border-primary/10 max-w-md">
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-primary text-sm">👤</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-sidebar-foreground truncate">{user.username}</p>
                    <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                  </div>
                </div>
                <button
                  onClick={onLogout}
                  className="w-full bg-background hover:bg-muted text-foreground border border-border rounded-lg px-4 py-2 text-sm font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
