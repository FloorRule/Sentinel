// DashboardContent.tsx
import { Chart } from "./Chart";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { LogsTable } from "./LogsTable";
import type { DashboardStats, Log, ChartPoint } from "./types";
import { useEffect, useState } from "react";

const INIT_STATS: DashboardStats = { total_vol: 0, threats_detected: 0, error_rate: 0 };

export function DashboardContent() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [chartData, setChartData] = useState<ChartPoint[]>([]);
  const [stats, setStats] = useState<DashboardStats>(INIT_STATS);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/dashboard");

    ws.onopen = () => {
      console.log("WS Connected");
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "logs")
          // so memory not explode
          setLogs((prev) => [msg.data, ...prev].slice(0, 100));
        else if (msg.type === "stats")
          setStats(msg.data);
        else if (msg.type === "chart-data")
          setChartData(msg.data);
        
      } catch (err) {
        console.error("Failed to parse WS message", err);
      }
    };

    ws.onerror = (err) => console.error("WS Error:", err);
    ws.onclose = () => {
      console.log("WS Closed");
      setIsConnected(false);
    };

    return () => ws.close();
  }, []);

  return (
    <div className="flex flex-col space-y-6">
      {/* live */}
      <div className="flex items-center justify-between border-b pb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight">Telemetry Stream</h2>
          <p className="text-xs text-muted-foreground">Live inference on incoming HTTP requests</p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs">
          <span
            className={`h-2 w-2 rounded-full ${isConnected ? "bg-emerald-500 animate-ping" : "bg-amber-500"}`}/>
          <span className="text-muted-foreground">
            {isConnected ? "WS Connected" : "Connecting..."}
          </span>
        </div>
      </div>

      {/* cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Total Traffic
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-extrabold font-mono tracking-tight">
              {stats.total_vol.toLocaleString()}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">Requests processed</p>
          </CardContent>
        </Card>

        <Card
          className={`shadow-sm transition-colors ${stats.threats_detected > 0 ? "border-red-200 bg-red-50/20" : ""}`}>

          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Threats Flagged
            </CardTitle>
            {stats.threats_detected > 0 && (
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-red-500"></span>
              </span>
            )}
          </CardHeader>
          <CardContent>
            <div
              className={`text-3xl font-extrabold font-mono tracking-tight ${stats.threats_detected > 0 ? "text-red-600" : "text-slate-900"}`}>
              {stats.threats_detected}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">Flagged by anomaly detector</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Error Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-extrabold font-mono tracking-tight">
              {stats.error_rate}%
            </div>
            <p className="mt-1 text-xs text-muted-foreground">HTTP 4xx / 5xx responses</p>
          </CardContent>
        </Card>
      </div>

      {/* chart*/}
      <Card className="shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-semibold">Throughput Over Time</CardTitle>
          <CardDescription className="text-xs">
            Success vs error volume in 1-minute aggregations
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-0">
          <Chart data={chartData} />
        </CardContent>
      </Card>

      {/* log */}
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base font-semibold">Live Event Log</CardTitle>
              <CardDescription className="text-xs">
                Real-time pipeline ingestion feed
              </CardDescription>
            </div>
            <span className="font-mono text-[11px] text-muted-foreground">
              {logs.length} events buffered
            </span>
          </div>
        </CardHeader>
        <CardContent>
          <LogsTable logs={logs} />
        </CardContent>
      </Card>
    </div>
  );
}