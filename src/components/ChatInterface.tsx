import { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, FileText, MessageCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { ScrollArea } from './ui/scroll-area';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isPattern?: boolean;
}

interface ChatInterfaceProps {
  chatHistory: ChatMessage[];
  onSendMessage: (message: string) => void;
}

export function ChatInterface({ chatHistory, onSendMessage }: ChatInterfaceProps) {
  const [message, setMessage] = useState('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-border p-6 bg-gradient-to-r from-primary/15 to-primary/5">
        <h2 className="text-xl font-medium flex items-center gap-3 text-primary-foreground">
          <div className="w-8 h-8 bg-primary/20 rounded-2xl flex items-center justify-center">
            <Sparkles className="h-4 w-4 text-primary-foreground" />
          </div>
          AI Pattern Assistant
        </h2>
        <p className="text-sm text-primary-foreground/80 mt-2 leading-relaxed">
          Transform complex crochet notation into easy-to-follow, cozy instructions
        </p>
      </div>

      <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
        <div className="space-y-4 max-w-4xl">
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
                  <div className="flex-1">
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
                    <div className="prose prose-sm">
                      <p className="whitespace-pre-wrap leading-relaxed text-card-foreground">{msg.content}</p>
                    </div>
                  </div>
                </div>
              </Card>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="border-t border-border p-6 bg-gradient-to-r from-card/80 to-card/60 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Paste your crochet pattern or ask a question..."
            className="flex-1 rounded-2xl border-primary/30 focus:border-primary/50 bg-input-background/80 text-foreground placeholder:text-muted-foreground"
          />
          <Button type="submit" disabled={!message.trim()} className="rounded-2xl px-6">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}