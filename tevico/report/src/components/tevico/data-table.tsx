import React, { useState, useEffect } from "react";
import {
    Table,
    TableHeader,
    TableBody,
    TableRow,
    TableHead,
    TableCell,
    TableCaption,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"; // Card components from shadcn
import { Select, SelectItem, SelectTrigger, SelectContent, SelectValue } from "@/components/ui/select"; // Select components
import { Pagination } from "@/components/ui/pagination"; // Pagination component

interface TableProps<T> {
    columns: { Header: string; accessor: keyof T }[];
    data: T[];
    filterKeys: (keyof T)[];
}

function DataTable<T>({ columns, data, filterKeys }: TableProps<T>) {
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedFilterKey, setSelectedFilterKey] = useState<keyof T | null>(null);
    const [filteredData, setFilteredData] = useState<T[]>(data);
    const [currentPage, setCurrentPage] = useState(1);
    const [rowsPerPage, setRowsPerPage] = useState(5);

    useEffect(() => {
        const lowerCaseQuery = searchQuery.toLowerCase();
        const filtered = data.filter((item) => {
            // If no filter key is selected, check all keys
            if (!selectedFilterKey) {
                return filterKeys.some((key) => {
                    const value = item[key];
                    return (
                        typeof value === "string" &&
                        value.toLowerCase().includes(lowerCaseQuery)
                    );
                });
            }
            // If a specific filter key is selected, check only that key
            const value = item[selectedFilterKey];
            return (
                typeof value === "string" &&
                value.toLowerCase().includes(lowerCaseQuery)
            );
        });

        setFilteredData(filtered);
        setCurrentPage(1); // Reset to page 1 on search change
    }, [searchQuery, data, filterKeys, selectedFilterKey]);

    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
    const paginatedData = filteredData.slice(
        (currentPage - 1) * rowsPerPage,
        currentPage * rowsPerPage
    );

    const handleChangePage = (newPage: number) => {
        if (newPage >= 1 && newPage <= totalPages) {
            setCurrentPage(newPage);
        }
    };

    return (
        <Card className="w-full shadow-md border rounded-lg">
            <CardHeader>
                <CardTitle className="text-lg font-semibold">Data Table</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="mb-4 flex justify-between items-center">
                    <Input
                        placeholder="Search..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-1/3"
                    />
                    <Select onValueChange={(value) => setSelectedFilterKey(value as keyof T)}>
                        <SelectTrigger className="w-1/4">
                            <SelectValue placeholder="Select Checks" />
                        </SelectTrigger>
                        <SelectContent>
                            {filterKeys.map((key) => (
                                <SelectItem key={key as string} value={key as string}>
                                    {key}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <Table className="w-full border border-gray-300">
                    <TableHeader>
                        <TableRow>
                            {columns.map((col) => (
                                <TableHead key={col.accessor as string} className="border p-2">
                                    {col.Header}
                                </TableHead>
                            ))}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {paginatedData.length > 0 ? (
                            paginatedData.map((item, index) => (
                                <TableRow key={index}>
                                    {columns.map((col) => (
                                        <TableCell key={col.accessor as string} className="border p-2">
                                            {item[col.accessor]}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={columns.length} className="text-center border p-2">
                                    No data found
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>

                <div className="flex justify-between items-center mt-4">
                    <Button
                        onClick={() => handleChangePage(currentPage - 1)}
                        disabled={currentPage === 1}
                    >
                        Previous
                    </Button>
                    <span>
                        Page {currentPage} of {totalPages}
                    </span>
                    <Button
                        onClick={() => handleChangePage(currentPage + 1)}
                        disabled={currentPage === totalPages}
                    >
                        Next
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}

export default DataTable;
