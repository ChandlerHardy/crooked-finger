'use client';

interface SettingsPageProps {
  user?: { id: string; username: string; email: string } | null;
  onLogout?: () => void;
}

export function SettingsPage({ user, onLogout }: SettingsPageProps) {
  return (
    <div className="h-full overflow-y-scroll p-6">
      <div className="w-full space-y-6">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Settings</h1>
          <p className="text-muted-foreground">Customize your Crooked Finger experience</p>
        </div>

        <div className="max-w-3xl mx-auto space-y-6">
          {/* AI Info */}
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-semibold mb-1">AI</h2>
              <p className="text-sm text-muted-foreground">Powered by z.ai</p>
            </div>
            <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-2xl p-4 border border-primary/10 max-w-md">
              <p className="text-sm text-sidebar-foreground">
                Pattern translation and chat are handled by the z.ai Anthropic-compatible proxy.
                No configuration needed — just use the app.
              </p>
            </div>
          </div>

          {/* Account */}
          {user && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold mb-1">Account</h2>
                <p className="text-sm text-muted-foreground">Manage your account</p>
              </div>
              <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-2xl p-4 border border-primary/10 max-w-md">
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-primary text-sm">👤</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-sidebar-foreground truncate">{user.username}</p>
                    <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                  </div>
                </div>
                <button
                  onClick={onLogout}
                  className="w-full bg-background hover:bg-muted text-foreground border border-border rounded-lg px-4 py-2 text-sm font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
