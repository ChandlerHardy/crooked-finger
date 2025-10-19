import { Home, MessageCircle, FolderOpen, BookOpen, Settings, Youtube, LogIn } from 'lucide-react';
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

      {!user && (
        <div className="p-4 border-t border-sidebar-border">
          <Button
            variant="default"
            size="sm"
            onClick={onLoginClick}
            className="w-full gap-2"
          >
            <LogIn className="h-4 w-4" />
            Sign In
          </Button>
        </div>
      )}
    </div>
  );
}