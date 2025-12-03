import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./components/ui/table"
import { Badge } from "./components/ui/badge"
import { ScrollArea } from "./components/ui/scroll-area"

// Log
type Log = {
  id: string
  timestamp: string
  level: "INFO" | "WARNING" | "ERROR" | "CRITICAL"
  service: string
  message: string
  statusCode: number
}

// Mock Data 
const logs: Log[] = [
  { id: "1", timestamp: "2023-10-25 10:23:45", level: "ERROR", service: "auth-service", message: "Invalid password attempt for user admin", statusCode: 401 },
  { id: "2", timestamp: "2023-10-25 10:23:42", level: "INFO", service: "payment-api", message: "Transaction verified successfully", statusCode: 200 },
  { id: "3", timestamp: "2023-10-25 10:23:40", level: "CRITICAL", service: "database", message: "Connection timeout at 192.168.1.5", statusCode: 500 },
  { id: "4", timestamp: "2023-10-25 10:23:35", level: "WARNING", service: "rate-limiter", message: "Rate limit approached for IP 10.0.0.1", statusCode: 429 },
  { id: "5", timestamp: "2023-10-25 10:23:30", level: "INFO", service: "frontend", message: "Page load complete: /dashboard", statusCode: 200 },
]

export function LogsTable() {
  return (
    <ScrollArea className="h-[400px] w-full rounded-md border">
      <Table>
        <TableHeader className="sticky top-0 bg-secondary">
          <TableRow>
            <TableHead className="w-[100px]">Time</TableHead>
            <TableHead className="w-[100px]">Level</TableHead>
            <TableHead className="w-[150px]">Service</TableHead>
            <TableHead>Message</TableHead>
            <TableHead className="text-right">Code</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => (
            <TableRow key={log.id}>
              
              {/* Timestamp */}
              <TableCell className="font-mono text-xs text-muted-foreground">
                {log.timestamp.split(" ")[1]} 
              </TableCell>

              {/* Status Badge */}
              <TableCell>
                <Badge 
                  variant="outline" 
                  className={`
                    ${log.level === 'CRITICAL' || log.level === 'ERROR' ? 'text-red-500 border-red-500 bg-red-50 dark:bg-red-950/20' : ''}
                    ${log.level === 'WARNING' ? 'text-orange-500 border-orange-500 bg-orange-50 dark:bg-orange-950/20' : ''}
                    ${log.level === 'INFO' ? 'text-blue-500 border-blue-500 bg-blue-50 dark:bg-blue-950/20' : ''}
                  `}
                >
                  {log.level}
                </Badge>
              </TableCell>

              <TableCell className="text-sm font-medium">{log.service}</TableCell>
              
              <TableCell className="font-mono text-xs text-muted-foreground max-w-[400px] truncate" title={log.message}>
                {log.message}
              </TableCell>

              <TableCell className="text-right font-mono text-xs">
                {log.statusCode}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </ScrollArea>
  )
}