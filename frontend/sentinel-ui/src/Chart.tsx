"use client"

import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"

import {
  type ChartConfig, 
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "./components/ui/chart"
import type { ChartPoint } from "./types"


const chartConfig = {
  success: {
    label: "Success",
    color: "#22c55e",
  },
  error: {
    label: "Error",
    color: "#ef4444",
  },
} satisfies ChartConfig

export function Chart({ data }: { data: ChartPoint[] }) {
  return (
    <ChartContainer config={chartConfig} className="h-[200px] w-full">
      <BarChart accessibilityLayer data={data}>
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="time"
          tickLine={false}
          tickMargin={10}
          axisLine={false}
        />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
        <Bar dataKey="success" fill="var(--color-success)" radius={4} />
        <Bar dataKey="error" fill="var(--color-error)" radius={4} />
      </BarChart>
    </ChartContainer>
  )
}
