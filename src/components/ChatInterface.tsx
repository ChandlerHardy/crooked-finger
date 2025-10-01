import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, Sparkles, FileText, MessageCircle, Image as ImageIcon, X, Paperclip } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card } from './ui/card';
import { ScrollArea } from './ui/scroll-area';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isPattern?: boolean;
  diagramSvg?: string;
  diagramPng?: string;
}

interface ChatInterfaceProps {
  chatHistory: ChatMessage[];
  onSendMessage: (message: string) => void;
  loading?: boolean;
  hideHeader?: boolean;
}

export function ChatInterface({ chatHistory, onSendMessage, loading = false, hideHeader = false }: ChatInterfaceProps) {
  const [message, setMessage] = useState('');
  const [pastedImages, setPastedImages] = useState<string[]>([]);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handlePaste = async (e: React.ClipboardEvent) => {
    const items = e.clipboardData.items;
    const newImages: string[] = [];

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.indexOf('image') !== -1) {
        e.preventDefault();
        const blob = item.getAsFile();
        if (blob) {
          const reader = new FileReader();
          reader.onload = (event) => {
            if (event.target?.result) {
              newImages.push(event.target.result as string);
              setPastedImages(prev => [...prev, event.target!.result as string]);
            }
          };
          reader.readAsDataURL(blob);
        }
      }
    }
  };

  const removeImage = (index: number) => {
    setPastedImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      Array.from(files).forEach((file) => {
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = (event) => {
            if (event.target?.result) {
              setPastedImages(prev => [...prev, event.target!.result as string]);
            }
          };
          reader.readAsDataURL(file);
        }
      });
    }
    // Reset file input so the same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() || pastedImages.length > 0) {
      // For now, just send the text message
      // TODO: Backend integration for image support
      let fullMessage = message;
      if (pastedImages.length > 0) {
        fullMessage += `\n\n[${pastedImages.length} image(s) attached - Image support coming soon!]`;
      }
      onSendMessage(fullMessage);
      setMessage('');
      setPastedImages([]);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {!hideHeader && (
        <div className="border-b border-border p-6 bg-gradient-to-r from-primary/15 to-primary/5">
          <h2 className="text-xl font-medium flex items-center gap-3 text-primary-foreground">
            <div className="w-8 h-8 bg-primary/20 rounded-2xl flex items-center justify-center">
              <Sparkles className="h-4 w-4 text-primary-foreground" />
            </div>
            GRANNi
          </h2>
          <p className="text-sm text-primary-foreground/80 mt-2 leading-relaxed">
            Transform complex crochet notation into easy-to-follow, cozy instructions
          </p>
        </div>
      )}

      <ScrollArea className="flex-1 p-6 overflow-auto" ref={scrollAreaRef}>
        <div className="space-y-4 max-w-4xl mx-auto min-h-full">
          {chatHistory.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageCircle className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium mb-2">Start a conversation</h3>
              <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                Paste your crochet pattern or ask me to explain any crochet notation. 
                I can help translate abbreviations and create readable instructions.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg mx-auto">
                <Button 
                  variant="outline" 
                  className="h-auto p-6 text-left flex-col items-start gap-3 rounded-2xl border-primary/30 hover:border-primary/50 hover:bg-primary/10 text-foreground hover:text-foreground"
                  onClick={() => onSendMessage("What does 'sc2tog' mean in crochet?")}
                >
                  <div className="w-8 h-8 bg-primary/20 rounded-xl flex items-center justify-center">
                    <span className="text-primary-foreground text-sm">❓</span>
                  </div>
                  <div>
                    <span className="font-medium">Explain notation</span>
                    <span className="text-xs text-muted-foreground block mt-1 leading-relaxed">Ask about crochet abbreviations</span>
                  </div>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-auto p-6 text-left flex-col items-start gap-3 rounded-2xl border-primary/30 hover:border-primary/50 hover:bg-primary/10 text-foreground hover:text-foreground"
                  onClick={() => onSendMessage("Translate this pattern: R1: ch 3, dc in 4th ch from hook, *ch 1, skip 1 ch, dc in next ch* repeat across")}
                >
                  <div className="w-8 h-8 bg-primary/20 rounded-xl flex items-center justify-center">
                    <span className="text-primary-foreground text-sm">✨</span>
                  </div>
                  <div>
                    <span className="font-medium">Translate pattern</span>
                    <span className="text-xs text-muted-foreground block mt-1 leading-relaxed">Convert notation to instructions</span>
                  </div>
                </Button>
              </div>
            </div>
          ) : (
            chatHistory.map((msg) => (
              <Card key={msg.id} className={`p-5 shadow-lg border-border/30 rounded-2xl backdrop-blur-sm ${
                msg.type === 'user' 
                  ? 'ml-12 bg-gradient-to-r from-primary/15 to-primary/8 border-primary/30' 
                  : 'mr-12 bg-card/90'
              }`}>
                <div className="flex items-start gap-4">
                  <div className={`w-9 h-9 rounded-2xl flex items-center justify-center ${
                    msg.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
                  }`}>
                    {msg.type === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="flex-1 min-w-0 overflow-hidden">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="font-medium text-card-foreground">
                        {msg.type === 'user' ? 'You' : 'AI Assistant'}
                      </span>
                      {msg.isPattern && (
                        <div className="flex items-center gap-1 text-xs bg-primary/20 text-primary-foreground px-2 py-1 rounded-full border border-primary/30">
                          <FileText className="h-3 w-3" />
                          Pattern
                        </div>
                      )}
                      <span className="text-xs text-muted-foreground">
                        {msg.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="prose prose-sm max-w-none overflow-hidden">
                      <div className="leading-relaxed text-card-foreground markdown-content break-words max-w-full">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            // Customize styling for specific elements
                            h1: (props) => <h1 className="text-xl font-bold mb-3 text-card-foreground break-words" {...props} />,
                            h2: (props) => <h2 className="text-lg font-semibold mb-2 text-card-foreground break-words" {...props} />,
                            h3: (props) => <h3 className="text-base font-medium mb-2 text-card-foreground break-words" {...props} />,
                            p: (props) => <p className="mb-2 text-card-foreground break-words" {...props} />,
                            strong: (props) => <strong className="font-semibold text-card-foreground" {...props} />,
                            em: (props) => <em className="italic text-card-foreground" {...props} />,
                            ul: (props) => <ul className="mb-2 ml-4 list-disc text-card-foreground" {...props} />,
                            ol: (props) => <ol className="mb-2 ml-4 list-decimal text-card-foreground" {...props} />,
                            li: (props) => <li className="mb-1 text-card-foreground break-words" {...props} />,
                            code: (props) => {
                              // Extract actual text content - ReactMarkdown passes string directly
                              const content = typeof props.children === 'string' ? props.children : String(props.children || '');


                              // TODO: Chart generation temporarily disabled - see CLAUDE.md for details
                              // SVG chart rendering needs better detection logic to avoid duplicate rendering
                              // Current issue: SVG fragments show as both code and rendered charts

                              // Temporarily disabled SVG detection
                              if (false) {
                                return null;
                              }
                              return <code className="bg-muted px-1 py-0.5 rounded text-sm font-mono text-card-foreground break-all max-w-full inline-block" {...props} />;
                            },
                            pre: (props) => {
                              // Extract text from pre block (usually contains a code element)
                              const extractText = (children: React.ReactNode): string => {
                                if (typeof children === 'string') return children;
                                if (React.isValidElement(children) && children.props?.children) {
                                  return extractText(children.props.children);
                                }
                                return String(children || '');
                              };

                              const content = extractText(props.children);


                              // TODO: Chart generation temporarily disabled - see CLAUDE.md for details
                              // SVG chart rendering needs better detection logic to avoid duplicate rendering
                              // Current issue: SVG fragments show as both code and rendered charts

                              // Temporarily disabled SVG detection
                              if (false) {
                                return null;
                              }
                              return <pre className="bg-muted p-2 rounded text-sm font-mono overflow-x-auto text-card-foreground break-all max-w-full" {...props} />;
                            },
                            blockquote: (props) => <blockquote className="border-l-4 border-primary pl-4 italic text-muted-foreground break-words" {...props} />
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                      {msg.diagramSvg && (
                        <div className="mt-6 p-4 bg-white rounded-lg border border-border/30 shadow-sm">
                          <h4 className="text-sm font-medium text-gray-700 mb-3">Pattern Diagram</h4>
                          <div
                            className="diagram-container flex justify-center items-center"
                            dangerouslySetInnerHTML={{ __html: msg.diagramSvg }}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            ))
          )}
          {loading && (
            <Card className="mr-12 bg-card/90 p-5 shadow-lg border-border/30 rounded-2xl backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="w-9 h-9 rounded-2xl flex items-center justify-center bg-muted text-muted-foreground">
                  🤖
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="font-medium text-card-foreground">AI Assistant</span>
                    <span className="text-xs text-muted-foreground">thinking...</span>
                  </div>
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

      <div className="border-t border-border p-6 bg-gradient-to-r from-card/80 to-card/60 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileSelect}
            className="hidden"
          />
          
          {/* Attached Images Preview */}
          {pastedImages.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {pastedImages.map((image, index) => (
                <div key={index} className="relative group">
                  <img 
                    src={image} 
                    alt={`Attached ${index + 1}`} 
                    className="h-20 w-20 object-cover rounded-xl border-2 border-primary/30"
                  />
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
          
          <div className="flex gap-3 items-center">
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={handleAttachClick}
              disabled={loading}
              className="rounded-2xl border-primary/30 hover:border-primary/50 hover:bg-primary/10 flex-shrink-0"
              title="Attach images"
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onPaste={handlePaste}
                placeholder="Type a message, paste or attach images..."
                className="rounded-2xl border-primary/30 focus:border-primary/50 bg-input-background/80 text-foreground placeholder:text-muted-foreground min-h-[44px] max-h-32 resize-none pr-10 !field-sizing-auto"
                style={{ 
                  wordBreak: 'break-word', 
                  whiteSpace: 'pre-wrap', 
                  overflowWrap: 'anywhere',
                  overflow: 'hidden'
                }}
                wrap="soft"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
              />
              {pastedImages.length > 0 && (
                <div className="absolute right-3 top-3 flex items-center gap-1 text-xs text-primary">
                  <ImageIcon className="h-3 w-3" />
                  <span>{pastedImages.length}</span>
                </div>
              )}
            </div>
            <Button type="submit" disabled={(!message.trim() && pastedImages.length === 0) || loading} className="rounded-2xl px-6 flex-shrink-0">
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}