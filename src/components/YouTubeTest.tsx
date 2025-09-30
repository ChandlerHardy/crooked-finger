'use client';

import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2 } from 'lucide-react';

export function YouTubeTest() {
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
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
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Example Crochet Tutorial URLs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <p className="text-muted-foreground">Try these popular crochet tutorials:</p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Search YouTube for "crochet granny square tutorial"</li>
                <li>Look for videos with closed captions enabled</li>
                <li>Note: Not all videos have transcripts available</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
