// DashboardLayout.tsx
import { DashboardContent } from "./DashboardContent";

export default function DashboardLayout() {
  return (
    <div className="min-h-screen bg-slate-50/60 font-sans text-slate-900 antialiased">

      <header className="sticky top-0 z-10 border-b bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-sm font-black text-white shadow-sm">
              S
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold tracking-tight text-slate-900">Sentinel</h1>
                <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-mono font-medium text-slate-600 border border-slate-200">
                  v1.0-dev
                </span>
              </div>
              <p className="text-xs text-muted-foreground hidden sm:block">
                ML-Powered Realtime Threat Analysis
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono">
            <span className="hidden md:inline">pipeline: /ws/dashboard</span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        
        <DashboardContent />
      </main>
    </div>
  );
}