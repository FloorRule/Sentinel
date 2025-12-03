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
import type { Log } from "./types"


export function LogsTable({ logs }: { logs: Log[] }) {
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
                {new Date(log.timestamp).toLocaleTimeString()}
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