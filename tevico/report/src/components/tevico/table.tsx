import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import Link from "next/link"
import { Button } from "../ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";

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
}

export function TableComponent(props: Props) {
    // return (
    //     <Card>
    //         <CardHeader className="flex flex-row items-center">
    //             <div className="grid gap-2">
    //                 <CardTitle>Transactions</CardTitle>
    //                 <CardDescription>
    //                     Recent transactions from your store.
    //                 </CardDescription>
    //             </div>
    //             <Button asChild size="sm" className="ml-auto gap-1">
    //                 {/* <Link href="#">
    //                     View All
    //                     <ArrowUpRight className="h-4 w-4" />
    //                 </Link> */}
    //             </Button>
    //         </CardHeader>
    //         <CardContent>
    //             <div>
    //                 <DataTable data={data} columns={columns} dropdownFilter={filters} searchBarFilter={searchBarFilter} />
    //             </div>
    //         </CardContent>
    //     </Card>
    // )
    return (
        <Card>
            <CardHeader className="flex flex-row items-center">
                <div className="grid gap-2">
                    <CardTitle>Transactions</CardTitle>
                    <CardDescription>
                        Recent transactions from your store.
                    </CardDescription>
                </div>
                <Button asChild size="sm" className="ml-auto gap-1">
                    {/* <Link href="#">
                        View All
                        <ArrowUpRight className="h-4 w-4" />
                    </Link> */}
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