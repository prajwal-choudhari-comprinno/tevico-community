
import { DollarSign } from 'lucide-react';

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card';

import { Progress } from '@/components/ui/progress';

interface MetricCardProps {
  title: string;
  value: number;
  content?: string;
}

export function MetricCard(props: MetricCardProps) {
  return (
    <Card x-chunk="dashboard-01-chunk-0">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          {props.title}
        </CardTitle>
        <DollarSign className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{props.value}</div>
        {
          props.content && (
            <CardDescription className="text-sm text-muted-foreground">
              {props.content}
            </CardDescription>
          )
        }
      </CardContent>
    </Card>
  );
};

