import { Chart } from "./Chart"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card"
import { LogsTable } from "./LogsTable"
import type { DashboardStats,Log,ChartPoint } from "./types"
import { useEffect, useState } from "react"

const INIT_STATS = { total_vol: 0, threats_detected: 0, error_rate: 0 }

export function DashboardContent() {
  const [logs, setLogs] = useState<Log[]>([])
  const [chartData, setChartData] = useState<ChartPoint[]>([])
  const [stats, setStats] = useState<DashboardStats>(INIT_STATS)


  const fetchData = async () => {
    try {
        
        // Fetch recent logs
        const logsRes = await fetch("http://localhost:8000/api/logs")
        const logsJson = await logsRes.json()
        setLogs(logsJson.result)

        // Fetch Stats
        const statsRes = await fetch("http://localhost:8000/api/stats")
        const statsJson = await statsRes.json()
        setStats(statsJson.result)

        // Fetch Chart Data
        const chartRes = await fetch("http://localhost:8000/api/chart-data")
        const chartJson = await chartRes.json()
        setChartData(chartJson.result)

    } catch (error) {
        console.error("Failed to fetch dashboard data:", error)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 2000) // Poll every 2 seconds
    return () => clearInterval(interval) // Cleanup
  }, [])

  return (
    <div className="flex flex-col space-y-6">
      
      {/* SECTION A: KPI CARDS */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_vol}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Threats Detected</CardTitle>
            {stats.threats_detected > 0 && <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{stats.threats_detected}</div>
            <p className="text-xs text-muted-foreground">High severity anomalies</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
             <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.error_rate}%</div>
          </CardContent>
        </Card>
      </div>

      {/* SECTION B: THE INTERACTIVE BAR CHART */}
      <div className="grid gap-4 md:grid-cols-1">
        <Card>
          <CardHeader>
            <CardTitle>Traffic Overview</CardTitle>
            <CardDescription>Requests per second over the last 30 minutes</CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <Chart data={chartData}/>
          </CardContent>
        </Card>
      </div>

      {/* SECTION C: THE TABLE */}
      <div className="grid gap-4 md:grid-cols-1">
        <Card>
          <CardHeader>
              <CardTitle>Recent Logs</CardTitle>
              <CardDescription>Live incoming stream from Redis</CardDescription>
          </CardHeader>
          <CardContent>
              <LogsTable logs={logs}/>
          </CardContent>
        </Card>
      </div>
      
    </div>
  )
}