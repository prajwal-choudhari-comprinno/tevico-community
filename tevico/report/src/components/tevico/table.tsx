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

interface Props {
    tableData: TableData;
    tableHeading: string;
    tableDescription?: string;
}

export function TableComponent(props: Props) {
    return (
        <Card>
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
                                <TableRow>
                                    {props.tableData.headers.map((e => (
                                        <TableCell>
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