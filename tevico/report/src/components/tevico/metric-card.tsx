
import { DollarSign, Info, Users } from 'lucide-react';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { HoverCard, HoverCardContent, HoverCardTrigger } from '../ui/hover-card';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';

interface MetricCardProps {
  title: string;
  value: number | string;
  content?: string;
}

export function MetricCard(props: MetricCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium basis-2/3 xl:basis-5/6">
          {props.title}
        </CardTitle>
        <div className='basis-auto'>
          <HoverCard>
            <HoverCardTrigger className='cursor-not-allowed'>
              <Button variant="icon" size="sm">
                <Info className="h-4 w-4 text-muted-foreground" />
              </Button>
            </HoverCardTrigger>
            <HoverCardContent className="w-80">
              <div className="flex justify-between space-x-4">
                <Avatar>
                  <AvatarImage src="https://github.com/vercel.png" />
                  <AvatarFallback>VC</AvatarFallback>
                </Avatar>
                <div className="space-y-1">
                  <h4 className="text-sm font-semibold">@nextjs</h4>
                  <p className="text-sm">
                    The React Framework – created and maintained by @vercel.
                  </p>
                  <div className="flex items-center pt-2">
                    <Info className="mr-2 h-4 w-4 opacity-70" />{" "}
                    <span className="text-xs text-muted-foreground">
                      Joined December 2021
                    </span>
                  </div>
                </div>
              </div>
            </HoverCardContent>
          </HoverCard>
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

