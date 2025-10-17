/* eslint-disable @next/next/no-img-element */
'use client';

import { useState, useRef } from 'react';
import { Send, X, Paperclip, Sparkles, FileText } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { isPdf } from '../lib/pdfToImage';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  images?: string[]; // Store attached images with the message
}

interface PatternCreationAIProps {
  onPatternExtracted: (data: {
    name?: string;
    notation?: string;
    instructions?: string;
    difficulty?: string;
    materials?: string;
    estimatedTime?: string;
    images?: string[];
  }) => void;
}

export function PatternCreationAI({ onPatternExtracted }: PatternCreationAIProps) {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [attachedImages, setAttachedImages] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && attachedImages.length < 5) {
      const remainingSlots = 5 - attachedImages.length;
      const filesToProcess = Array.from(files).slice(0, remainingSlots);

      for (const file of filesToProcess) {
        // Handle images directly, but convert PDFs to images first
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = (event) => {
            if (event.target?.result) {
              setAttachedImages(prev => [...prev, event.target!.result as string]);
            }
          };
          reader.readAsDataURL(file);
        } else if (file.type === 'application/pdf') {
          // Convert PDF to JPEG before storing
          try {
            const { convertPdfToImage } = await import('../lib/pdfToImage');
            const pdfDataUrl = URL.createObjectURL(file);
            const imageDataUrl = await convertPdfToImage(pdfDataUrl);
            
            // Clean up object URL
            URL.revokeObjectURL(pdfDataUrl);
            
            setAttachedImages(prev => [...prev, imageDataUrl]);
          } catch (error) {
            console.error('Error converting PDF to image:', error);
            // Fallback to trying to save the PDF as-is if conversion fails
            const reader = new FileReader();
            reader.onload = (event) => {
              if (event.target?.result) {
                setAttachedImages(prev => [...prev, event.target!.result as string]);
              }
            };
            reader.readAsDataURL(file);
          }
        }
      }
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeImage = (index: number) => {
    setAttachedImages(prev => prev.filter((_, i) => i !== index));
  };

  // Helper function to detect if base64 string is a PDF
  const isPDF = (base64String: string): boolean => {
    try {
      // Use the utility function
      return isPdf(base64String);
    } catch {
      // Fallback implementation in case the utility is not available
      console.log('🔍 Checking if PDF:', base64String.substring(0, 50));

      if (base64String.startsWith('data:application/pdf')) {
        console.log('✅ Detected PDF via data URL prefix');
        return true;
      }
      if (base64String.startsWith('JVBERi0')) {
        console.log('✅ Detected PDF via magic bytes');
        return true;
      }
      if (base64String.startsWith('/9j/')) {
        console.log('❌ Detected JPEG, not PDF');
        return false; // Definitely a JPEG
      }

      try {
        const decoded = atob(base64String.substring(0, 8));
        const result = decoded.startsWith('%PDF');
        console.log(result ? '✅ Detected PDF via base64 decode' : '❌ Not a PDF');
        return result;
      } catch (e) {
        console.log('❌ Failed to decode base64, not a PDF');
        return false;
      }
    }
  };

  const extractPatternFromResponse = (response: string) => {
    console.log('📋 Full AI Response:', response);
    console.log('📋 First 200 chars:', response.substring(0, 200));

    // Remove model prefix like "[gemini-2.5-pro]" from the beginning of response
    const cleanResponse = response.replace(/^\[[\w\-\.]+\]\s*/i, '').trim();
    console.log('🧹 Cleaned response (first 200):', cleanResponse.substring(0, 200));

    const extractSection = (text: string, headers: string[]): string | undefined => {
      for (const header of headers) {
        // More flexible regex - handles various formats including markdown bold, numbering, etc.
        // Matches: "NAME:", "**NAME:**", "1. NAME:", etc.
        const headerPattern = `(?:^|\\n)(?:[0-9]+\\.)?\\s*(?:\\*\\*)?${header}(?:\\*\\*)?\\s*:`;
        const headerRegex = new RegExp(headerPattern, 'i');
        const match = text.match(headerRegex);

        if (match && match.index !== undefined) {
          const startIndex = match.index + match[0].length;
          const afterHeader = text.substring(startIndex);

          // Find the next section header (more flexible pattern)
          const nextSectionPattern = /\n(?:[0-9]+\.)?\s*(?:\*\*)?(NAME|NOTATION|INSTRUCTIONS|DIFFICULTY|MATERIALS|TIME)(?:\*\*)?\s*:/i;
          const nextMatch = afterHeader.match(nextSectionPattern);

          let content: string;
          if (nextMatch && nextMatch.index !== undefined) {
            content = afterHeader.substring(0, nextMatch.index);
          } else {
            content = afterHeader;
          }

          // Clean up the content - remove leading/trailing whitespace and markdown
          content = content.trim();
          // Remove leading asterisks or other markdown if present
          content = content.replace(/^\*\*(.+?)\*\*$/, '$1').trim();

          if (content) {
            console.log(`✅ Extracted '${header}': ${content.substring(0, 50)}...`);
            return content;
          }
        }
      }
      return undefined;
    };

    let extractedName = extractSection(cleanResponse, ['NAME', 'Pattern Name', 'Name', 'Title', 'TITLE', 'Pattern']);

    // If NAME is still not found, try to extract from the first line if it looks like a title
    if (!extractedName) {
      // Check if first line looks like a pattern name (not a field header)
      const firstLine = cleanResponse.split('\n')[0].trim();
      if (firstLine &&
          !firstLine.match(/^(NAME|NOTATION|INSTRUCTIONS|DIFFICULTY|MATERIALS|TIME):/i) &&
          firstLine.length < 100) {
        console.log('📝 Using first line as name:', firstLine);
        extractedName = firstLine;
      }
    }

    const extractedNotation = extractSection(cleanResponse, ['NOTATION', 'Pattern Notation', 'Notation']);
    const extractedInstructions = extractSection(cleanResponse, ['INSTRUCTIONS', 'Detailed Instructions', 'Instructions', 'Steps', 'STEPS']);
    const extractedDifficulty = extractSection(cleanResponse, ['DIFFICULTY', 'Difficulty Level', 'Skill Level', 'Level']);
    const extractedMaterials = extractSection(cleanResponse, ['MATERIALS', 'Supplies', 'Materials Needed', 'Yarn', 'YARN']);
    const extractedTime = extractSection(cleanResponse, ['TIME', 'Estimated Time', 'Duration', 'Completion Time']);

    console.log('📊 Extraction Results:', {
      name: extractedName,
      notation: extractedNotation ? extractedNotation.substring(0, 50) + '...' : undefined,
      instructions: extractedInstructions ? extractedInstructions.substring(0, 50) + '...' : undefined,
      difficulty: extractedDifficulty,
      materials: extractedMaterials ? extractedMaterials.substring(0, 50) + '...' : undefined,
      time: extractedTime
    });

    // Normalize difficulty to match expected values
    let normalizedDifficulty: string | undefined = undefined;
    if (extractedDifficulty) {
      const lower = extractedDifficulty.toLowerCase();
      if (lower.includes('beginner')) normalizedDifficulty = 'beginner';
      else if (lower.includes('intermediate')) normalizedDifficulty = 'intermediate';
      else if (lower.includes('advanced')) normalizedDifficulty = 'advanced';
    }

    // Only call the callback if we extracted at least one field
    if (extractedName || extractedNotation || extractedInstructions) {
      onPatternExtracted({
        name: extractedName,
        notation: extractedNotation,
        instructions: extractedInstructions,
        difficulty: normalizedDifficulty,
        materials: extractedMaterials,
        estimatedTime: extractedTime,
        images: attachedImages.length > 0 ? attachedImages : undefined,
      });
    }
  };

  const handleSendMessage = async () => {
    console.log('🚀 handleSendMessage called, attachedImages.length:', attachedImages.length);
    if (!message.trim() && attachedImages.length === 0) return;

    // Build context message with system prompt
    let contextMessage = `SYSTEM CONTEXT: You are an AI assistant embedded in a pattern creation form. Your responses will be automatically parsed to populate the pattern fields. When the user provides pattern information (via text or images), respond in this EXACT format:

NAME: [Pattern name - descriptive title like "Granny Square" or "Simple Beanie"]
NOTATION: [Abbreviated crochet notation using standard abbreviations like ch, dc, sc, etc.]
INSTRUCTIONS: [Full step-by-step instructions in plain English with line breaks between rounds/rows]
DIFFICULTY: [beginner, intermediate, or advanced]
MATERIALS: [Yarn weight, hook size, and supplies]
TIME: [Estimated completion time]

IMPORTANT: Use this exact format with these exact header names. The app will extract these sections and auto-populate the pattern creation form.

`;

    if (message.trim()) {
      contextMessage += `USER REQUEST: ${message}`;
    } else if (attachedImages.length > 0) {
      contextMessage += 'USER REQUEST: Please analyze these pattern files (images/PDFs) and populate the pattern fields with the extracted information.';
    }

    // Add user message to chat history (store images before they're cleared)
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message || '📎 Attached files for pattern analysis',
      timestamp: new Date(),
      images: attachedImages.length > 0 ? [...attachedImages] : undefined, // Copy images
    };

    console.log('💬 Adding user message to chat with images:', userMessage.images?.length, 'images');
    if (userMessage.images && userMessage.images.length > 0) {
      console.log('💬 First image:', userMessage.images[0].substring(0, 50));
    }

    setChatHistory(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);

    try {
      const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://150.136.38.166:8001/crooked-finger/graphql';

      // Get auth token from localStorage
      const authToken = typeof window !== 'undefined' ? localStorage.getItem('crooked-finger-token') : null;

      const variables: Record<string, unknown> = {
        message: contextMessage,
        context: 'crochet_pattern_assistant',
      };

      // Convert images array to JSON string (matching iOS implementation)
      if (attachedImages.length > 0) {
        const base64Images = attachedImages.map(img => {
          // Remove data URL prefix (e.g., "data:image/png;base64,")
          return img.includes(',') ? img.split(',')[1] : img;
        });
        // Send as JSON string, not array - this matches iOS
        variables.imageData = JSON.stringify(base64Images);
      }

      const response = await fetch(graphqlUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
        },
        body: JSON.stringify({
          query: `
            mutation ChatWithAssistantEnhanced($message: String!, $context: String, $imageData: String) {
              chatWithAssistantEnhanced(message: $message, context: $context, imageData: $imageData) {
                message
                hasPattern
              }
            }
          `,
          variables,
        }),
      });

      const result = await response.json();

      if (result.data?.chatWithAssistantEnhanced) {
        const aiResponse = result.data.chatWithAssistantEnhanced;

        // Add assistant message to chat history
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: aiResponse.message,
          timestamp: new Date(),
        };

        setChatHistory(prev => [...prev, assistantMessage]);

        // Extract pattern fields from response
        extractPatternFromResponse(aiResponse.message);

        // Clear attached images after successful send
        setAttachedImages([]);
      } else if (result.errors) {
        console.error('GraphQL errors:', result.errors);
        throw new Error(result.errors[0]?.message || 'Failed to get AI response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px]">
      {/* Chat Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4 min-h-full">
          {chatHistory.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-lg font-medium mb-2">AI Pattern Assistant</h3>
              <p className="text-sm text-muted-foreground max-w-md mx-auto">
                Upload images or PDFs of crochet patterns, or describe what you&apos;d like to create.
                I&apos;ll help extract the pattern details and fill in the form for you.
              </p>
            </div>
          ) : (
            chatHistory.map((msg) => (
              <Card key={msg.id} className={`p-4 ${
                msg.type === 'user'
                  ? 'ml-12 bg-primary/10'
                  : 'mr-12 bg-card'
              }`}>
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    msg.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                  }`}>
                    {msg.type === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm mb-1">
                      {msg.type === 'user' ? 'You' : 'AI Assistant'}
                    </div>
                    <div className="text-sm whitespace-pre-wrap break-words">
                      {msg.content}
                    </div>
                    {/* Display attached images in chat message */}
                    {msg.images && msg.images.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {msg.images.map((image, idx) => {
                          const isPdf = isPDF(image);
                          console.log(`🖼️ Rendering image ${idx}: isPDF=${isPdf}, first 50 chars:`, image.substring(0, 50));
                          return (
                          <div key={idx}>
                            {isPdf ? (
                              <div className="h-16 w-16 rounded-lg border-2 border-primary overflow-hidden bg-white relative">
                                <object
                                  data={image}
                                  type="application/pdf"
                                  className="w-full h-full pointer-events-none"
                                >
                                  <div className="w-full h-full flex flex-col items-center justify-center bg-primary/10">
                                    <FileText className="h-8 w-8 text-primary mb-1" />
                                    <span className="text-[10px] font-semibold text-primary">PDF</span>
                                  </div>
                                </object>
                              </div>
                            ) : (
                              <img
                                src={image}
                                alt={`Attached ${idx + 1}`}
                                className="h-16 w-16 object-cover rounded-lg border-2 border-primary/30"
                                onError={(e) => {
                                  // If image fails to load, show placeholder
                                  e.currentTarget.style.display = 'none';
                                  const parent = e.currentTarget.parentElement;
                                  if (parent) {
                                    const placeholder = document.createElement('div');
                                    placeholder.className = 'h-16 w-16 flex items-center justify-center rounded-lg border-2 border-primary/30 bg-muted';
                                    placeholder.innerHTML = '<svg class="h-10 w-10 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>';
                                    parent.appendChild(placeholder);
                                  }
                                }}
                              />
                            )}
                          </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))
          )}
          {loading && (
            <Card className="mr-12 bg-card p-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full flex items-center justify-center bg-muted">
                  🤖
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm mb-2">AI Assistant</div>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            </Card>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t p-4 bg-card">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="space-y-3"
        >
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,application/pdf"
            multiple
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Attached Images Preview */}
          {attachedImages.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {attachedImages.map((image, index) => (
                <div key={index} className="relative group">
                  {isPDF(image) ? (
                    <div className="h-20 w-20 rounded-lg border-2 border-primary overflow-hidden bg-white">
                      <object
                        data={image}
                        type="application/pdf"
                        className="w-full h-full pointer-events-none"
                      >
                        <div className="w-full h-full flex flex-col items-center justify-center bg-primary/10">
                          <FileText className="h-10 w-10 text-primary mb-1" />
                          <span className="text-[10px] font-semibold text-primary">PDF</span>
                        </div>
                      </object>
                    </div>
                  ) : (
                    <img
                      src={image}
                      alt={`Attached ${index + 1}`}
                      className="h-20 w-20 object-cover rounded-lg border-2 border-primary/30"
                      onError={(e) => {
                        // If image fails to load, show placeholder
                        e.currentTarget.style.display = 'none';
                        const parent = e.currentTarget.parentElement;
                        if (parent) {
                          const placeholder = document.createElement('div');
                          placeholder.className = 'h-20 w-20 flex items-center justify-center rounded-lg border-2 border-primary/30 bg-muted';
                          placeholder.innerHTML = '<svg class="h-10 w-10 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>';
                          parent.appendChild(placeholder);
                        }
                      }}
                    />
                  )}
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="absolute -top-2 -right-2 bg-destructive text-destructive-foreground rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2 items-end">
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              disabled={loading || attachedImages.length >= 5}
              className="flex-shrink-0"
              title={attachedImages.length >= 5 ? 'Maximum 5 files' : 'Attach images or PDFs'}
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Describe the pattern or ask a question..."
              className="resize-none"
              rows={2}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <Button
              type="submit"
              disabled={(!message.trim() && attachedImages.length === 0) || loading}
              className="flex-shrink-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>

          <p className="text-xs text-muted-foreground">
            {attachedImages.length > 0
              ? `${attachedImages.length}/5 files attached`
              : 'Tip: Upload images or PDFs of patterns for automatic extraction'}
          </p>
        </form>
      </div>
    </div>
  );
}
