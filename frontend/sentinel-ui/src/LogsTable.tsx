// LogsTable.tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./components/ui/table";
import { Badge } from "./components/ui/badge";
import { ScrollArea } from "./components/ui/scroll-area";
import type { Log } from "./types";

export function LogsTable({ logs }: { logs: Log[] }) {
  if (logs.length === 0) {
    return (
      <div className="flex h-[250px] w-full flex-col items-center justify-center rounded-md border border-dashed text-center">
        <p className="font-mono text-sm text-muted-foreground">Waiting for events...</p>
        <p className="text-xs text-muted-foreground/70">Connect backend server to see live logs.</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-[380px] w-full rounded-md border">
      <Table>
        <TableHeader className="sticky top-0 bg-slate-100/90 backdrop-blur-sm shadow-sm">
          <TableRow className="border-b">
            <TableHead className="w-[110px] text-xs font-mono">TIMESTAMP</TableHead>
            <TableHead className="w-[90px] text-xs font-mono">SEVERITY</TableHead>
            <TableHead className="w-[140px] text-xs font-mono">SERVICE</TableHead>
            <TableHead className="text-xs font-mono">MESSAGE</TableHead>
            <TableHead className="w-[80px] text-right text-xs font-mono">CODE</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log, idx) => (
            <TableRow key={log.id || `${log.timestamp}-${idx}`} className="hover:bg-slate-50/80">
              <TableCell className="font-mono text-xs text-slate-500 whitespace-nowrap">
                {new Date(log.timestamp).toLocaleTimeString()}
              </TableCell>

              <TableCell>
                <Badge
                  variant="outline"
                  className={`font-mono text-[10px] tracking-wide px-1.5 py-0 ${
                    log.level === "CRITICAL" || log.level === "ERROR"
                      ? "border-red-300 bg-red-50 text-red-700"
                      : log.level === "WARNING"
                      ? "border-amber-300 bg-amber-50 text-amber-700"
                      : "border-blue-300 bg-blue-50 text-blue-700"}`}>
                  {log.level}
                </Badge>
              </TableCell>

              <TableCell className="text-xs font-medium font-mono text-slate-700">
                {log.service}
              </TableCell>

              <TableCell className="font-mono text-xs text-slate-600 max-w-[360px] truncate"
                title={log.message}>
                  
                {log.message}
              </TableCell>

              <TableCell className="text-right font-mono text-xs font-semibold">
                <span
                  className={
                    log.statusCode >= 500
                      ? "text-red-600"
                      : log.statusCode >= 400
                      ? "text-amber-600"
                      : "text-emerald-600"
                  }
                >
                  {log.statusCode}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </ScrollArea>
  );
}