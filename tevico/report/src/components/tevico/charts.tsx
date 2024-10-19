"use client"

import { Bar, BarChart, CartesianGrid, Cell, Label, Pie, PieChart, Tooltip, XAxis, YAxis } from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import React from "react";
import { TrendingUp } from "lucide-react";

type ChartDataPoint = {
  [key: string]: number | string;
};

type ChartConfig = {
  xAxis: string;
  dataKeys: string[];
};

type ChartData = {
  data: ChartDataPoint[];
  config: ChartConfig;
};

type PieChartDataPoint = {
  [key: string]: number;
};

type PieChartConfig = {
  labelKey: string;
  valueKey: string;
  titleKey?: string;
};

export type PieChartData = {
  data: PieChartDataPoint;
  config: PieChartConfig;
};

interface ChartProps {
  type: "BAR" | "HORIZONTAL_BAR" | "PIE" | "PIE_WITH_STATS" | "DOUGHNUT",
  barChartData?: ChartData,
  horizontalBarChartData?: ChartData,
  pieChartData?: PieChartData,
  pieChartWithStatsData?: PieChartData,
  doughnutChartData?: PieChartData,
  cardTitle: string;
  cardDescription?: string;
  cardType?: string;
}

const chartHeight: number = 250;
const barChartWidth: number = 400;
const pieChartWidth: number = 500;

export function generateChartColor() {
  const hue = 137 + Math.floor(Math.random() * 6);
  const saturation = 40 + Math.floor(Math.random() * 49);
  const lightness = 9 + Math.floor(Math.random() * 36);
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

const BarChartComponent = ({ chartData }: { chartData: ChartData }) => (
  <BarChart width={barChartWidth} height={chartHeight} accessibilityLayer data={chartData.data}>
    <CartesianGrid vertical={false} />
    <XAxis
      dataKey={chartData.config.xAxis}
      tickLine={false}
      tickMargin={10}
      axisLine={false}
      tickFormatter={(value) => value.toString().slice(0, 3)}
    />
    {chartData.config.dataKeys.map((key, index) => (
      <Bar key={key} dataKey={key} fill={`hsl(var(--chart-${index + 1}))` || generateChartColor()} radius={8} />
    ))}
  </BarChart>
);

const HorizontalBarChartComponent = ({ chartData }: { chartData: ChartData }) => (
  <BarChart width={barChartWidth} height={chartHeight}
    accessibilityLayer
    data={chartData.data}
    layout="vertical"
    margin={{ left: -10 }}
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
      <Bar key={key} dataKey={key} fill={`hsl(var(--chart-${index + 1}))` || generateChartColor()} radius={5} />
    ))}
  </BarChart>
);

const PieChartComponent = ({ chartData }: { chartData: PieChartData }) => {
  const dataAsArray = Object.keys(chartData.data).map(key => Object.assign({
    [chartData.config.labelKey]: key,
    [chartData.config.valueKey]: chartData.data[key]
  }));
  return (
    <PieChart width={pieChartWidth} height={chartHeight}>
      <Pie
        data={dataAsArray}
        dataKey={chartData.config.valueKey}
        nameKey={chartData.config.labelKey}
        label={({ payload, ...props }) => {
          return (
            <text
              cx={props.cx}
              cy={props.cy}
              x={props.x}
              y={props.y}
              textAnchor={props.textAnchor}
              dominantBaseline={props.dominantBaseline}
              fill="hsla(var(--foreground))"
            >
              {`${payload[chartData.config.labelKey]} (${payload[chartData.config.valueKey]})`}
            </text>
          )
        }}
      >
        {dataAsArray.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={`hsl(var(--chart-${index + 1}))` || `hsl(${index * 45}, 70%, 60%)`} />
        ))}
      </Pie>
      <Tooltip />
    </PieChart >
  )
};

const PieV2ChartComponent = ({ chartData }: { chartData: PieChartData }) => {
  const dataAsArray = Object.keys(chartData.data).map(key => Object.assign({
    [chartData.config.labelKey]: key,
    [chartData.config.valueKey]: chartData.data[key]
  }));
  const totalCount = React.useMemo(() => {
    const key: string = chartData.config.valueKey;
    return dataAsArray.reduce((acc, curr) => acc + (curr[key] || 0), 0);
  }, [chartData.config.valueKey, chartData.data]);

  return (
    <PieChart width={pieChartWidth} height={chartHeight}>
      <Pie
        data={dataAsArray}
        dataKey={chartData.config.valueKey}
        nameKey={chartData.config.labelKey}
        innerRadius={60}
        label={({ payload, ...props }) => {
          return (
            <text
              cx={props.cx}
              cy={props.cy}
              x={props.x}
              y={props.y}
              textAnchor={props.textAnchor}
              dominantBaseline={props.dominantBaseline}
              fill="hsla(var(--foreground))"
            >
              {`${payload[chartData.config.labelKey]} (${payload[chartData.config.valueKey]})`}
            </text>
          )
        }}
      >
        <Label
          content={({ viewBox }) => {
            if (viewBox && "cx" in viewBox && "cy" in viewBox) {
              return (
                <text
                  x={viewBox.cx}
                  y={viewBox.cy}
                  textAnchor="middle"
                  dominantBaseline="middle"
                >
                  <tspan
                    x={viewBox.cx}
                    y={viewBox.cy}
                    className="fill-foreground text-xl font-bold"
                  >
                    {totalCount.toLocaleString()}
                  </tspan>
                  <tspan
                    x={viewBox.cx}
                    y={(viewBox.cy || 0) + 24}
                    className="fill-muted-foreground"
                  >
                    {chartData.config.titleKey}
                  </tspan>
                </text>
              )
            }
          }}
        />
        {dataAsArray.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={`hsl(var(--chart-${index + 1}))` || `hsl(${index * 45}, 70%, 60%)`} />
        ))}
      </Pie>
    </PieChart>
  )
};

const DoughnutChartComponent = ({ chartData }: { chartData: PieChartData }) => {
  const dataAsArray = Object.keys(chartData.data).map(key => Object.assign({
    [chartData.config.labelKey]: key,
    [chartData.config.valueKey]: chartData.data[key]
  }));
  return (
    <PieChart width={pieChartWidth} height={chartHeight}>
      <Pie
        data={dataAsArray}
        dataKey={chartData.config.valueKey}
        nameKey={chartData.config.labelKey}
        innerRadius={60}
        label={({ payload, ...props }) => {
          return (
            <text
              cx={props.cx}
              cy={props.cy}
              x={props.x}
              y={props.y}
              textAnchor={props.textAnchor}
              dominantBaseline={props.dominantBaseline}
              fill="hsla(var(--foreground))"
            >
              {`${payload[chartData.config.labelKey]} (${payload[chartData.config.valueKey]})`}
            </text>
          )
        }}
      >
        {dataAsArray.map((_, index) => (
          <Cell key={`cell-${index}`} fill={`hsl(var(--chart-${index + 1}))` || `hsl(${index * 45}, 70%, 60%)`} />
        ))}
      </Pie>
    </PieChart>
  )
};

export function Chart(props: ChartProps) {
  const renderChart = React.useMemo(() => {
    switch (props.type) {
      case 'BAR':
        return props.barChartData && <BarChartComponent chartData={props.barChartData} />;
      case 'HORIZONTAL_BAR':
        return props.horizontalBarChartData && <HorizontalBarChartComponent chartData={props.horizontalBarChartData} />;
      case 'PIE':
        return props.pieChartData && <PieChartComponent chartData={props.pieChartData} />;
      case 'DOUGHNUT':
        return props.doughnutChartData && <DoughnutChartComponent chartData={props.doughnutChartData} />;
      case 'PIE_WITH_STATS':
        return props.pieChartWithStatsData && <PieV2ChartComponent chartData={props.pieChartWithStatsData} />;
      default:
        return null;
    }
  }, [props.type, props.barChartData, props.horizontalBarChartData, props.pieChartData, props.doughnutChartData, props.pieChartWithStatsData]);

  const { cardType } = props;
  const style: React.CSSProperties = {};

  if (cardType === 'Error') {
    style.backgroundColor = 'rgba(255, 0, 0, 0.05)';
  }

  return (
    <Card className="flex flex-col" style={style}>
      <CardHeader>
        <CardTitle>{props.cardTitle}</CardTitle>
        {
          props.cardDescription && (
            <CardDescription className="text-sm text-muted-foreground">
              {props.cardDescription}
            </CardDescription>
          )
        }
      </CardHeader>
      <CardContent className="flex-1 flex justify-center items-center gap-2 text-sm">
        {renderChart}
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
  );

}