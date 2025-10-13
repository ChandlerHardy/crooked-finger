import { Home, MessageCircle, FolderOpen, BookOpen, Settings, Activity, Youtube, LogIn, LogOut, User } from 'lucide-react';
import { Button } from './ui/button';
import { ThemeToggle } from './ThemeToggle';
import Image from 'next/image';

interface NavigationProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  user?: { id: string; username: string; email: string } | null;
  onLoginClick?: () => void;
  onLogoutClick?: () => void;
}

export function Navigation({ currentPage, onPageChange, user, onLoginClick, onLogoutClick }: NavigationProps) {
  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'chat', label: 'AI Assistant', icon: MessageCircle },
    { id: 'projects', label: 'My Projects', icon: FolderOpen },
    { id: 'patterns', label: 'Pattern Library', icon: BookOpen },
    { id: 'youtube-test', label: 'YouTube Test', icon: Youtube },
    { id: 'usage', label: 'AI Usage', icon: Activity },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="w-64 bg-sidebar border-r border-sidebar-border h-full flex flex-col shadow-sm">
      <div className="w-64 h-64 border-b border-sidebar-border flex items-center justify-center">
        <Image 
          src="/CFC-logo-3.png" 
          alt="Crooked Finger Crochet" 
          width={240} 
          height={240}
          className="rounded-xl"
        />
      </div>
      
      <nav className="flex-1 p-4 flex flex-col">
        <ul className="space-y-3 flex-1">
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
        <div className="mt-4 flex justify-center">
          <ThemeToggle />
        </div>
      </nav>

      <div className="p-4 border-t border-sidebar-border space-y-3">
        {/* User section */}
        {user ? (
          <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-2xl p-4 border border-primary/10">
            <div className="flex items-start gap-3 mb-3">
              <div className="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <User className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-sidebar-foreground truncate">{user.username}</p>
                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={onLogoutClick}
              className="w-full gap-2"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </Button>
          </div>
        ) : (
          <Button
            variant="default"
            size="sm"
            onClick={onLoginClick}
            className="w-full gap-2"
          >
            <LogIn className="h-4 w-4" />
            Sign In
          </Button>
        )}

        {/* AI info section */}
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