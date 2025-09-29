import { Home, MessageCircle, FolderOpen, BookOpen, Settings, Activity } from 'lucide-react';
import { Button } from './ui/button';
import { ThemeToggle } from './ThemeToggle';

interface NavigationProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

export function Navigation({ currentPage, onPageChange }: NavigationProps) {
  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'chat', label: 'AI Assistant', icon: MessageCircle },
    { id: 'projects', label: 'My Projects', icon: FolderOpen },
    { id: 'patterns', label: 'Pattern Library', icon: BookOpen },
    { id: 'usage', label: 'AI Usage', icon: Activity },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="w-64 bg-sidebar border-r border-sidebar-border h-full flex flex-col shadow-sm">
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary rounded-xl flex items-center justify-center">
              <span className="text-primary-foreground font-medium">🧶</span>
            </div>
            <h1 className="text-xl font-medium text-sidebar-foreground">Crooked Finger</h1>
          </div>
          <ThemeToggle />
        </div>
        <p className="text-sm text-muted-foreground">Your cozy pattern assistant</p>
      </div>
      
      <nav className="flex-1 p-4">
        <ul className="space-y-3">
          {navigationItems.map((item) => (
            <li key={item.id}>
              <Button
                variant={currentPage === item.id ? 'default' : 'ghost'}
                className={`w-full justify-start gap-3 h-12 rounded-2xl transition-all duration-200 ${
                  currentPage === item.id 
                    ? 'bg-primary text-primary-foreground shadow-md' 
                    : 'hover:bg-sidebar-accent text-sidebar-foreground'
                }`}
                onClick={() => onPageChange(item.id)}
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </Button>
            </li>
          ))}
        </ul>
      </nav>
      
      <div className="p-4 border-t border-sidebar-border">
        <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-2xl p-4 border border-primary/10">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-primary/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-primary text-xs">✨</span>
            </div>
            <div>
              <p className="text-sm font-medium text-sidebar-foreground mb-1">AI-Powered</p>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Transform complex crochet notation into easy-to-follow instructions
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}