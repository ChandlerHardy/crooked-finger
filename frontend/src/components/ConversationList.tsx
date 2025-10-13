'use client';

import React from 'react';
import { MessageCircle, Plus, Trash2, MoreVertical } from 'lucide-react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

interface ChatConversation {
  id: string;
  title: string;
  messages: unknown[];
  createdAt: Date;
  updatedAt: Date;
}

interface ConversationListProps {
  conversations: ChatConversation[];
  activeConversationId: string | null;
  onConversationSelect: (conversationId: string) => void;
  onNewConversation: () => void;
  onDeleteConversation?: (conversationId: string) => void;
}

export function ConversationList({
  conversations,
  activeConversationId,
  onConversationSelect,
  onNewConversation,
  onDeleteConversation,
}: ConversationListProps) {
  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return new Date(date).toLocaleDateString();
  };

  return (
    <div className="w-80 border-r border-border bg-sidebar flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Conversations
          </h2>
          <Button
            size="sm"
            onClick={onNewConversation}
            className="gap-2"
          >
            <Plus className="h-4 w-4" />
            New
          </Button>
        </div>
      </div>

      {/* Conversation List */}
      <ScrollArea className="flex-1">
        {conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-6 text-center">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
              <MessageCircle className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              No conversations yet
            </p>
            <Button size="sm" onClick={onNewConversation} className="gap-2">
              <Plus className="h-4 w-4" />
              Start chatting
            </Button>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {conversations.map((conversation) => {
              const isActive = conversation.id === activeConversationId;
              const messageCount = conversation.messages?.length || 0;

              return (
                <div
                  key={conversation.id}
                  className={`group relative flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-muted'
                  }`}
                  onClick={() => onConversationSelect(conversation.id)}
                >
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 bg-primary/10">
                    <MessageCircle className={`h-4 w-4 ${isActive ? 'text-primary-foreground' : 'text-primary'}`} />
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-medium truncate ${isActive ? 'text-primary-foreground' : 'text-foreground'}`}>
                      {conversation.title || 'New Conversation'}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <p className={`text-xs ${isActive ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                        {messageCount} {messageCount === 1 ? 'message' : 'messages'}
                      </p>
                      <span className={`text-xs ${isActive ? 'text-primary-foreground/50' : 'text-muted-foreground/50'}`}>•</span>
                      <p className={`text-xs ${isActive ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                        {formatDate(conversation.updatedAt)}
                      </p>
                    </div>
                  </div>

                  {onDeleteConversation && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className={`opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 ${
                            isActive ? 'hover:bg-primary-foreground/10' : ''
                          }`}
                          onClick={(e) => e.stopPropagation()}
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteConversation(conversation.id);
                          }}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
