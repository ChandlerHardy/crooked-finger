import { useState } from 'react';
import { Search, Filter, BookOpen, Download, Heart, Eye } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';

interface Pattern {
  id: string;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: string;
  tags: string[];
  notation: string;
  instructions: string;
  isFavorite: boolean;
  views: number;
  downloads: number;
}

const mockPatterns: Pattern[] = [
  {
    id: '1',
    name: 'Granny Square',
    description: 'Classic granny square pattern perfect for beginners',
    difficulty: 'beginner',
    category: 'motifs',
    tags: ['square', 'classic', 'afghan'],
    notation: 'Ch 4, join with sl st to form ring. R1: Ch 3, 2 dc in ring, ch 2, *3 dc in ring, ch 2* 3 times, join.',
    instructions: 'Chain 4 and join with slip stitch to form a ring. Round 1: Chain 3 (counts as first double crochet), work 2 double crochets in ring, chain 2, repeat around...',
    isFavorite: true,
    views: 1250,
    downloads: 340
  },
  {
    id: '2',
    name: 'Shell Stitch Border',
    description: 'Elegant shell border for blankets and scarves',
    difficulty: 'intermediate',
    category: 'borders',
    tags: ['shell', 'border', 'decorative'],
    notation: '*Skip 2 sts, 5 dc in next st, skip 2 sts, sc in next st* repeat across',
    instructions: 'Skip 2 stitches, work 5 double crochets in the next stitch to create a shell, skip 2 stitches, single crochet in next stitch...',
    isFavorite: false,
    views: 890,
    downloads: 120
  },
  {
    id: '3',
    name: 'Cable Stitch Panel',
    description: 'Advanced cable technique for textured projects',
    difficulty: 'advanced',
    category: 'stitches',
    tags: ['cable', 'texture', 'advanced'],
    notation: 'FPtr around next 2 sts, skip next 2 sts behind FPtr, FPtr around skipped sts',
    instructions: 'Front post treble crochet around the next 2 stitches, skip the next 2 stitches behind the front post trebles, then work front post trebles around the skipped stitches to create the cable cross...',
    isFavorite: true,
    views: 650,
    downloads: 85
  },
];

export function PatternLibrary() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');

  const categories = ['all', 'motifs', 'borders', 'stitches', 'edgings', 'flowers'];
  const difficulties = ['all', 'beginner', 'intermediate', 'advanced'];

  const filteredPatterns = mockPatterns.filter(pattern => {
    const matchesSearch = pattern.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pattern.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pattern.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || pattern.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === 'all' || pattern.difficulty === selectedDifficulty;
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-emerald-100 text-emerald-800';
      case 'intermediate': return 'bg-orange-100 text-orange-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-border p-6">
        <div className="mb-6">
          <h2 className="text-xl font-medium flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Pattern Library
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Discover and save crochet patterns with AI translations
          </p>
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="relative flex-1 min-w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search patterns, tags, or techniques..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-input rounded-md bg-background text-foreground min-w-32"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
              </option>
            ))}
          </select>
          
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="px-3 py-2 border border-input rounded-md bg-background text-foreground min-w-32"
          >
            {difficulties.map(difficulty => (
              <option key={difficulty} value={difficulty}>
                {difficulty === 'all' ? 'All Levels' : difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex-1 p-6">
        {filteredPatterns.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <BookOpen className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">No patterns found</h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Try adjusting your search terms or filters to find what you're looking for.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredPatterns.map((pattern) => (
              <Card key={pattern.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-medium">{pattern.name}</h3>
                        {pattern.isFavorite && (
                          <Heart className="h-4 w-4 text-red-500 fill-red-500" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {pattern.description}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        <Badge className={getDifficultyColor(pattern.difficulty)}>
                          {pattern.difficulty}
                        </Badge>
                        <Badge variant="outline">{pattern.category}</Badge>
                        {pattern.tags.slice(0, 2).map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="pt-0">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Notation:</label>
                      <div className="mt-1 p-3 bg-muted/50 rounded-lg">
                        <code className="text-sm font-mono">{pattern.notation}</code>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Instructions:</label>
                      <p className="mt-1 text-sm leading-relaxed">{pattern.instructions}</p>
                    </div>
                    
                    <div className="flex items-center justify-between pt-2 border-t border-border">
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Eye className="h-3 w-3" />
                          {pattern.views}
                        </span>
                        <span className="flex items-center gap-1">
                          <Download className="h-3 w-3" />
                          {pattern.downloads}
                        </span>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button variant="ghost" size="sm">
                          <Heart className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button size="sm">
                          Use Pattern
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}