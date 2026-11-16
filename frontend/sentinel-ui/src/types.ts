export interface Log {
  id?: number;
  timestamp: string;
  service: string;
  level: string;
  message: string;
  endpoint?: string;
  status_code?: number;
  statusCode?: number;
  client_ip?: string;
  is_threat: boolean;
  risk_score: number;
  severity: "INFO" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
  tags?: string[];
  reasons?: string[];
}

export interface DashboardStats {
  total_vol: number;
  threats_detected: number;
  error_rate: number;
}

export interface ChartPoint {
  time: string;
  error: number;
  success: number;
}