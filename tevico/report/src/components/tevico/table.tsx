import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import Link from "next/link"
import { Button } from "../ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";
import { ArrowUpRight } from "lucide-react";

type headers = {
  key: string,
  label: string
}

type TableData = {
  headers: headers[],
  data: any[]
}

export interface TableProps {
  tableData: TableData;
  tableHeading: string;
  tableDescription?: string;
  cardType?: string;
}

export function TableComponent(props: TableProps) {
  const { cardType } = props;

  const style: React.CSSProperties = {};

  if (cardType === 'Error') {
    style.backgroundColor = 'rgba(255, 0, 0, 0.05)';
  } else if (cardType === 'Success') {
    style.backgroundColor = 'rgba(0, 255, 0, 0.05)';
  }

  return (
    <Card style={style}>
      <CardHeader className="flex flex-row items-center">
        <div className="grid gap-2">
          <CardTitle>{props.tableHeading}</CardTitle>
          {
            props.tableDescription && (
              <CardDescription>
                {props.tableDescription}
              </CardDescription>
            )
          }
        </div>
        <Button asChild size="sm" className="ml-auto gap-1">
          <a href="#">
            View All
            <ArrowUpRight className="h-4 w-4" />
          </a>
        </Button>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              {props.tableData.headers.map((header) => (
                <TableHead key={header.key}>{header.label}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {
              props.tableData.data.map((ele => (
                <TableRow key={(Math.random() + 1).toString(36).substring(5)}>
                  {props.tableData.headers.map((e => (
                    <TableCell key={e.key}>
                      <div className="font-medium">{ele[e.key]}</div>
                    </TableCell>
                  )))}
                </TableRow>
              )))
            }
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}