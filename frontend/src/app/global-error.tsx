'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body>
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            backgroundColor: '#fff',
            padding: '1rem',
          }}
        >
          <div style={{ textAlign: 'center', maxWidth: '28rem' }}>
            <div style={{ fontSize: '3.75rem', marginBottom: '1rem' }}>🧶</div>
            <h2
              style={{
                fontSize: '1.5rem',
                fontWeight: 600,
                color: '#111827',
                marginBottom: '0.5rem',
              }}
            >
              Something went wrong
            </h2>
            <p
              style={{
                color: '#6b7280',
                marginBottom: '1.5rem',
                lineHeight: 1.5,
              }}
            >
              We hit a snag — but don&apos;t worry, your data is safe. Try again
              or refresh the page.
            </p>
            <button
              onClick={reset}
              style={{
                padding: '0.625rem 1.25rem',
                backgroundColor: '#9333ea',
                color: '#fff',
                fontWeight: 500,
                borderRadius: '0.5rem',
                border: 'none',
                cursor: 'pointer',
                fontSize: '1rem',
              }}
            >
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
