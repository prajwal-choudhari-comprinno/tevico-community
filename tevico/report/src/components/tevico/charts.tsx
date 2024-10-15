"use client"

import { TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, XAxis, YAxis } from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type DataKey = string;
type DataValue = number | string;

type ChartDataPoint = {
  [key: DataKey]: DataValue;
};

type ChartConfig = {
  xAxis: DataKey;
  dataKeys: DataKey[];
};

type ChartData = {
  data: ChartDataPoint[];
  config: ChartConfig;
};

type PieChartConfig = {
  labelKey: DataKey;
  valueKey: DataKey;
};

type PieChartData = {
  data: ChartDataPoint[];
  config: PieChartConfig;
};

interface ChartProps {
  type: "BAR" | "HORIZONTAL_BAR" | "PIE" | "DOUGHNUT",
  barChartData?: ChartData,
  horizontalBarChartData?: ChartData,
  pieChartData?: PieChartData,
  doughnutChartData?: PieChartData,
}

const BarChartComponent = ({ chartData }: { chartData: ChartData }) => (
  <BarChart width={300} height={300} accessibilityLayer data={chartData.data}>
    <CartesianGrid vertical={false} />
    <XAxis
      dataKey={chartData.config.xAxis}
      tickLine={false}
      tickMargin={10}
      axisLine={false}
      tickFormatter={(value) => value.toString().slice(0, 3)}
    />
    {chartData.config.dataKeys.map((key, index) => (
      <Bar key={key} dataKey={key} fill={`hsl(var(--chart-${index + 1}))`} radius={8} />
    ))}
  </BarChart>
  // <ResponsiveContainer width="100%" height={300}>
  // </ResponsiveContainer>
);

const HorizontalBarChartComponent = ({ chartData }: { chartData: ChartData }) => (
  <BarChart width={300} height={300}
    accessibilityLayer
    data={chartData.data}
    layout="vertical"
    margin={{ left: -20 }}
  >
    <CartesianGrid horizontal={false} />
    <XAxis type="number" hide />
    <YAxis
      dataKey={chartData.config.xAxis}
      type="category"
      tickLine={false}
      tickMargin={10}
      axisLine={false}
      tickFormatter={(value) => value.toString().slice(0, 3)}
    />
    {chartData.config.dataKeys.map((key, index) => (
      <Bar key={key} dataKey={key} fill={`hsl(var(--chart-${index + 1}))`} radius={5} />
    ))}
  </BarChart>
  // <ResponsiveContainer width="100%" height={300}>
  // </ResponsiveContainer>
);

const PieChartComponent = ({ chartData }: { chartData: PieChartData }) => (
  <PieChart width={300} height={300}>
    <Pie
      data={chartData.data}
      dataKey={chartData.config.valueKey}
      nameKey={chartData.config.labelKey}
    >
      {chartData.data.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={`hsl(var(--chart-${index + 1}))` || `hsl(${index * 45}, 70%, 60%)`} />
      ))}
    </Pie>
  </PieChart>
  // <ResponsiveContainer width="100%" height={300}>
  // </ResponsiveContainer>
);

const DoughnutChartComponent = ({ chartData }: { chartData: PieChartData }) => (
  <PieChart width={300} height={300}>
    <Pie
      data={chartData.data}
      dataKey={chartData.config.valueKey}
      nameKey={chartData.config.labelKey}
      innerRadius={60}
      outerRadius={80}
      label
    >
      {chartData.data.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={`hsl(var(--chart-${index + 1}))` || `hsl(${index * 45}, 70%, 60%)`} />
      ))}
    </Pie>
  </PieChart>
  // <ResponsiveContainer width="100%" height={300}>
  // </ResponsiveContainer>
);

export function Chart(props: ChartProps) {
  const renderChart = () => {
    switch (props.type) {
      case 'BAR':
        return props.barChartData ? <BarChartComponent chartData={props.barChartData} /> : null;
      case 'HORIZONTAL_BAR':
        return props.horizontalBarChartData ? <HorizontalBarChartComponent chartData={props.horizontalBarChartData} /> : null;
      case 'PIE':
        return props.pieChartData ? <PieChartComponent chartData={props.pieChartData} /> : null;
      case 'DOUGHNUT':
        return props.doughnutChartData ? <DoughnutChartComponent chartData={props.doughnutChartData} /> : null;
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Chart</CardTitle>
        <CardDescription>January - June 2024</CardDescription>
      </CardHeader>
      <CardContent className="min-h-[300px]">
        {renderChart()}
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex gap-2 font-medium leading-none">
          Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
        </div>
        <div className="leading-none text-muted-foreground">
          Showing total visitors for the last 6 months
        </div>
      </CardFooter>
    </Card>
  )
}
