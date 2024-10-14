"use client"

import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"

interface ChartProps {
    chartData: any[]
}

export function CustomBarChart(props: ChartProps) {
    return (
        <BarChart width={250} height={300} accessibilityLayer data={props.chartData}>
            <CartesianGrid vertical={false} />
            <XAxis
                dataKey="month"
                tickLine={false}
                tickMargin={10}
                axisLine={false}
                tickFormatter={(value) => value.slice(0, 3)}
            />
            <Bar dataKey="desktop" fill="hsl(var(--chart-1))" radius={4} />
            <Bar dataKey="mobile" fill="hsl(var(--chart-2))" radius={4} />
        </BarChart>
    )
}