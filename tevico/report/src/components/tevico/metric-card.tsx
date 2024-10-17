
import { DollarSign, Users } from 'lucide-react';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';


interface MetricCardProps {
  icon: string,
  title: string;
  value: number;
  content?: string;
}

export function MetricCard(props: MetricCardProps) {
  return (
    <Card x-chunk="dashboard-01-chunk-0">
      <CardHeader className="flex flex-row justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium basis-2/3">
          {props.title}
        </CardTitle>
        <div className='basis-auto'>
          {(() => {
            switch (props.icon) {
              case 'users':
                return <Users className="h-4 w-4 text-muted-foreground" />;
              case 'dollar':
                return <DollarSign className="h-4 w-4 text-muted-foreground" />;
              default:
                null;
            }
          })()}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {props.value}
        </div>
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

