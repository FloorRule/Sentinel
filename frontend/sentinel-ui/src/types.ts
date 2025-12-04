export type DashboardStats = {
    total_vol: number
    threats_detected: number
    error_rate: number
}

export type ChartPoint = {
    time: string
    success: number
    error: number
}

export type Log = {
    id: string
    timestamp: string
    level: "INFO" | "WARNING" | "ERROR" | "CRITICAL"
    service: string
    message: string
    statusCode: number
}