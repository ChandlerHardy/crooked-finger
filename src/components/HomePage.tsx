import { Calendar, MessageCircle, FolderOpen, Sparkles, TrendingUp, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

interface Project {
  id: string;
  name: string;
  description: string;
  pattern: string;
  status: 'planning' | 'in-progress' | 'completed';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  isFavorite: boolean;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isPattern?: boolean;
}

interface HomePageProps {
  recentProjects: Project[];
  recentChats: ChatMessage[];
  onNavigate: (page: string) => void;
}

export function HomePage({ recentProjects, recentChats, onNavigate }: HomePageProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planning': return 'bg-blue-100 text-blue-800';
      case 'in-progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const stats = [
    {
      title: 'Active Projects',
      value: recentProjects.filter(p => p.status === 'in-progress').length,
      icon: FolderOpen,
      color: 'text-blue-600',
    },
    {
      title: 'Completed Projects',
      value: recentProjects.filter(p => p.status === 'completed').length,
      icon: TrendingUp,
      color: 'text-green-600',
    },
    {
      title: 'AI Translations',
      value: recentChats.filter(c => c.isPattern).length,
      icon: Sparkles,
      color: 'text-purple-600',
    },
    {
      title: 'This Week',
      value: recentProjects.filter(p => {
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        return p.updatedAt > weekAgo;
      }).length,
      icon: Clock,
      color: 'text-orange-600',
    },
  ];

  return (
    <div className="h-full overflow-auto">
      <div className="p-6">
        {/* Welcome Section */}
        <div className="mb-8 bg-gradient-to-r from-primary/15 to-primary/5 rounded-3xl p-6 border border-primary/20">
          <h1 className="text-2xl font-medium mb-2 text-primary-foreground">Welcome back! 🧶</h1>
          <p className="text-primary-foreground/80 leading-relaxed">
            Ready to continue your crochet journey? Here's what's happening with your cozy projects.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <Card key={stat.title} className="border-border/30 shadow-lg hover:shadow-xl transition-shadow duration-200 bg-card/90 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.title}</p>
                    <p className="text-2xl font-medium mt-1 text-card-foreground">{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-2xl bg-primary/20 ${stat.color}`}>
                    <stat.icon className="h-6 w-6 text-primary-foreground" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Projects */}
          <Card className="border-border/30 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-card-foreground">
                  <div className="w-8 h-8 bg-primary/20 rounded-xl flex items-center justify-center">
                    <FolderOpen className="h-4 w-4 text-primary-foreground" />
                  </div>
                  Recent Projects
                </CardTitle>
                <Button variant="ghost" size="sm" onClick={() => onNavigate('projects')} className="text-primary hover:text-primary hover:bg-primary/20 rounded-xl">
                  View all
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {recentProjects.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center mx-auto mb-3">
                    <FolderOpen className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">No projects yet</p>
                  <Button size="sm" onClick={() => onNavigate('projects')}>
                    Create your first project
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {recentProjects.slice(0, 3).map((project) => (
                    <div key={project.id} className="flex items-center justify-between p-4 bg-gradient-to-r from-muted/30 to-muted/10 rounded-2xl hover:from-muted/50 hover:to-muted/20 transition-all duration-200 cursor-pointer border border-border/30">
                      <div className="flex-1">
                        <h4 className="font-medium">{project.name}</h4>
                        <p className="text-sm text-muted-foreground line-clamp-1">
                          {project.description}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge className={`${getStatusColor(project.status)} rounded-full`} variant="secondary">
                            {project.status.replace('-', ' ')}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {project.updatedAt.toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent AI Chats */}
          <Card className="border-border/30 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-card-foreground">
                  <div className="w-8 h-8 bg-primary/20 rounded-xl flex items-center justify-center">
                    <MessageCircle className="h-4 w-4 text-primary-foreground" />
                  </div>
                  Recent GRANNi Chats
                </CardTitle>
                <Button variant="ghost" size="sm" onClick={() => onNavigate('chat')} className="text-primary hover:text-primary hover:bg-primary/20 rounded-xl">
                  View all
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {recentChats.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center mx-auto mb-3">
                    <MessageCircle className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">No conversations yet</p>
                  <Button size="sm" onClick={() => onNavigate('chat')}>
                    Start chatting with GRANNi
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {recentChats.slice(0, 3).map((chat) => (
                    <div key={chat.id} className="flex items-start gap-3 p-4 bg-gradient-to-r from-muted/30 to-muted/10 rounded-2xl hover:from-muted/50 hover:to-muted/20 transition-all duration-200 cursor-pointer border border-border/30">
                      <div className="w-8 h-8 rounded-2xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                        {chat.type === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm line-clamp-2">{chat.content}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {chat.isPattern && (
                            <Badge variant="outline" className="text-xs rounded-full border-primary/30 text-primary">
                              Pattern
                            </Badge>
                          )}
                          <span className="text-xs text-muted-foreground">
                            {chat.timestamp.toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className="mt-8 border-border/30 shadow-lg bg-card/90 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-card-foreground">
              <div className="w-6 h-6 bg-primary/20 rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground text-sm">⚡</span>
              </div>
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button 
                variant="outline" 
                className="h-auto p-6 flex-col gap-4 rounded-2xl border-primary/30 hover:border-primary/50 hover:bg-primary/10 transition-all duration-200 text-card-foreground hover:text-card-foreground"
                onClick={() => onNavigate('chat')}
              >
                <div className="w-12 h-12 bg-primary/20 rounded-2xl flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-primary-foreground" />
                </div>
                <div className="text-center">
                  <div className="font-medium">Translate Pattern</div>
                  <div className="text-xs text-muted-foreground leading-relaxed mt-1">Convert crochet notation to readable instructions</div>
                </div>
              </Button>
              
              <Button 
                variant="outline" 
                className="h-auto p-6 flex-col gap-4 rounded-2xl border-primary/30 hover:border-primary/50 hover:bg-primary/10 transition-all duration-200 text-card-foreground hover:text-card-foreground"
                onClick={() => onNavigate('projects')}
              >
                <div className="w-12 h-12 bg-primary/20 rounded-2xl flex items-center justify-center">
                  <FolderOpen className="h-6 w-6 text-primary-foreground" />
                </div>
                <div className="text-center">
                  <div className="font-medium">New Project</div>
                  <div className="text-xs text-muted-foreground leading-relaxed mt-1">Start tracking a new crochet project</div>
                </div>
              </Button>
              
              <Button 
                variant="outline" 
                className="h-auto p-6 flex-col gap-4 rounded-2xl border-primary/30 hover:border-primary/50 hover:bg-primary/10 transition-all duration-200 text-card-foreground hover:text-card-foreground"
                onClick={() => onNavigate('patterns')}
              >
                <div className="w-12 h-12 bg-primary/20 rounded-2xl flex items-center justify-center">
                  <Calendar className="h-6 w-6 text-primary-foreground" />
                </div>
                <div className="text-center">
                  <div className="font-medium">Browse Patterns</div>
                  <div className="text-xs text-muted-foreground leading-relaxed mt-1">Explore saved patterns and templates</div>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}