"use client"

import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";

interface ChartProps {
    chartData: any[]
}

const chartData = [
    { month: "January", desktop: 186 },
    { month: "February", desktop: 305 },
    { month: "March", desktop: 237 },
    { month: "April", desktop: 73 },
    { month: "May", desktop: 209 },
    { month: "June", desktop: 214 },
  ]

export function CustomHorBarChart(props: ChartProps) {
    return (
        <BarChart width={250} height={300}
            accessibilityLayer
            data={chartData}
            layout="vertical"
            margin={{
                left: -20,
            }}
        >
            <CartesianGrid horizontal={false} />
            <XAxis type="number" dataKey="desktop" hide />
            <YAxis
                dataKey="month"
                type="category"
                tickLine={false}
                tickMargin={10}
                axisLine={false}
                tickFormatter={(value) => value.slice(0, 3)}
            />
            {/* <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent hideLabel />}
            /> */}
            <Bar dataKey="desktop" fill="hsl(var(--chart-1))" radius={5} />
        </BarChart>
    )
}