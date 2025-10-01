'use client';

import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Sparkles } from 'lucide-react';

interface YouTubeTestProps {
  onNavigate?: (page: string) => void;
  onSavePattern?: (patternData: any) => void;
}

export function YouTubeTest({ onNavigate, onSavePattern }: YouTubeTestProps = {}) {
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [extractingPattern, setExtractingPattern] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [extractedPattern, setExtractedPattern] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFetchTranscript = async () => {
    if (!videoUrl.trim()) {
      setError('Please enter a YouTube URL');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://150.136.38.166:8001/crooked-finger/graphql';
      const response = await fetch(graphqlUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: `
            mutation FetchYouTubeTranscript($videoUrl: String!, $languages: [String!]) {
              fetchYoutubeTranscript(videoUrl: $videoUrl, languages: $languages) {
                success
                videoId
                transcript
                wordCount
                language
                thumbnailUrl
                thumbnailUrlHq
                error
              }
            }
          `,
          variables: {
            videoUrl,
            languages: ['en'],
          },
        }),
      });

      const data = await response.json();

      if (data.errors) {
        setError(data.errors[0].message);
      } else if (data.data?.fetchYoutubeTranscript) {
        const transcriptData = data.data.fetchYoutubeTranscript;
        if (transcriptData.success) {
          setResult(transcriptData);
        } else {
          setError(transcriptData.error || 'Failed to fetch transcript');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleExtractPattern = async () => {
    if (!result || !result.transcript) {
      setError('Please fetch a transcript first');
      return;
    }

    setExtractingPattern(true);
    setError(null);
    setExtractedPattern(null);

    try {
      const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://150.136.38.166:8001/crooked-finger/graphql';
      const response = await fetch(graphqlUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: `
            mutation ExtractPatternFromTranscript($transcript: String!, $videoId: String, $thumbnailUrl: String) {
              extractPatternFromTranscript(transcript: $transcript, videoId: $videoId, thumbnailUrl: $thumbnailUrl) {
                success
                patternName
                patternNotation
                patternInstructions
                difficultyLevel
                materials
                estimatedTime
                videoId
                thumbnailUrl
                error
              }
            }
          `,
          variables: {
            transcript: result.transcript,
            videoId: result.videoId,
            thumbnailUrl: result.thumbnailUrl,
          },
        }),
      });

      const data = await response.json();

      if (data.errors) {
        setError(data.errors[0].message);
      } else if (data.data?.extractPatternFromTranscript) {
        const patternData = data.data.extractPatternFromTranscript;
        if (patternData.success) {
          setExtractedPattern(patternData);
        } else {
          setError(patternData.error || 'Failed to extract pattern');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Network error occurred');
    } finally {
      setExtractingPattern(false);
    }
  };

  return (
    <div className="h-full overflow-auto p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">YouTube Transcript Test</h1>
          <p className="text-muted-foreground">
            Test fetching transcripts from YouTube videos (temporary testing page)
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Fetch Video Transcript</CardTitle>
            <CardDescription>
              Enter a YouTube URL to fetch its transcript. Try a crochet tutorial!
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="https://www.youtube.com/watch?v=..."
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !loading) {
                    handleFetchTranscript();
                  }
                }}
              />
              <Button
                onClick={handleFetchTranscript}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Fetching...
                  </>
                ) : (
                  'Fetch Transcript'
                )}
              </Button>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {result && (
              <div className="space-y-4">
                <Alert>
                  <AlertDescription>
                    ✅ Successfully fetched transcript!
                  </AlertDescription>
                </Alert>

                {result.thumbnailUrl && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Video Thumbnail</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <img
                        src={result.thumbnailUrl}
                        alt={`Thumbnail for video ${result.videoId}`}
                        className="w-full rounded-lg"
                        onError={(e) => {
                          // Fallback to HQ thumbnail if maxres fails
                          const target = e.target as HTMLImageElement;
                          if (result.thumbnailUrlHq && target.src !== result.thumbnailUrlHq) {
                            target.src = result.thumbnailUrlHq;
                          }
                        }}
                      />
                    </CardContent>
                  </Card>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Video ID</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="font-mono text-sm">{result.videoId}</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Word Count</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="font-mono text-sm">{result.wordCount?.toLocaleString()} words</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Language</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="font-mono text-sm">{result.language}</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Characters</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="font-mono text-sm">{result.transcript?.length.toLocaleString()} chars</p>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Transcript Preview</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="max-h-96 overflow-y-auto bg-muted rounded-md p-4">
                      <p className="text-sm whitespace-pre-wrap font-mono">
                        {result.transcript?.substring(0, 5000)}
                        {result.transcript?.length > 5000 && '...'}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <div className="flex justify-end">
                  <Button
                    onClick={handleExtractPattern}
                    disabled={extractingPattern}
                    size="lg"
                    className="gap-2"
                  >
                    {extractingPattern ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Extracting Pattern with AI...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-5 w-5" />
                        Extract Pattern with AI
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}

            {extractedPattern && (
              <Card className="border-primary">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary" />
                    Extracted Crochet Pattern
                  </CardTitle>
                  <CardDescription>
                    AI-generated pattern from video transcript
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {extractedPattern.patternName && (
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Pattern Name:</label>
                      <p className="mt-1 text-lg font-semibold">{extractedPattern.patternName}</p>
                    </div>
                  )}

                  {extractedPattern.difficultyLevel && (
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Difficulty:</label>
                      <p className="mt-1 capitalize">{extractedPattern.difficultyLevel}</p>
                    </div>
                  )}

                  {extractedPattern.materials && (
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Materials:</label>
                      <p className="mt-1 text-sm">{extractedPattern.materials}</p>
                    </div>
                  )}

                  {extractedPattern.estimatedTime && (
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Estimated Time:</label>
                      <p className="mt-1 text-sm">{extractedPattern.estimatedTime}</p>
                    </div>
                  )}

                  {extractedPattern.patternNotation && (
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Pattern Notation:</label>
                      <div className="mt-1 p-3 bg-muted/50 rounded-lg">
                        <code className="text-sm font-mono whitespace-pre-wrap">{extractedPattern.patternNotation}</code>
                      </div>
                    </div>
                  )}

                  {extractedPattern.patternInstructions && (
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Instructions:</label>
                      <p className="mt-1 text-sm leading-relaxed whitespace-pre-wrap">{extractedPattern.patternInstructions}</p>
                    </div>
                  )}

                  <div className="flex gap-2 pt-4 border-t">
                    <Button 
                      variant="outline" 
                      className="flex-1"
                      onClick={() => {
                        if (extractedPattern && onSavePattern) {
                          onSavePattern(extractedPattern);
                        }
                      }}
                    >
                      Save to Library
                    </Button>
                    <Button 
                      className="flex-1"
                      onClick={() => onNavigate?.('projects')}
                    >
                      Start Project
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
