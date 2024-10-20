"use client"
import { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip";
import "@/styles/globals.css";

import { DataTableColumnHeader } from "@/components/tevico/data-table/data-table-column-header";
import { CheckReport } from "../types/checkTypes";
import { providers, severity } from "./data/data";

export const columns: ColumnDef<CheckReport>[] = [
  {
    accessorKey: "title",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Title" />
    ),
    cell: ({ row }) => {
      const title = row.original.check_metadata?.check_title || "N/A";
      return (
        <div className="flex space-x-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <span className="truncate max-w-[500px] font-medium cursor-pointer block overflow-hidden whitespace-nowrap"
                >
                  {title}
                </span>
              </TooltipTrigger>
              <TooltipContent>
                <p>{title}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

        </div>
      )
    },
    enableSorting: false,
  },
  {
    accessorKey: "status",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Status" />
    ),
    cell: ({ row }) => {
      const passed = row.original.passed;
      const statusLabel = passed ? "Pass" : "Fail";
      const badgeColor = passed ? "bg-green-500" : "bg-red-500"; // Adjust colors as needed

      return (
        <div className="flex w-[100px] items-center">
          {statusLabel}
        </div>
      )
    },
    filterFn: (row, id, value) => {
      console.log(value);

      const passed = row.original.passed;
      const status = passed ? "pass" : "fail";
      return value.includes(status)
    },
    enableSorting: false,
  },
  {
    accessorKey: "severity",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Severity" />
    ),
    cell: ({ row }) => {
      const rowData = row.original.check_metadata?.severity || "N/A";
      const label = severity.find((d) => d.value === rowData)?.label
      if (!label) { return null }
      return (
        <div className="flex items-center">
          {label}
        </div>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.original.check_metadata?.severity)
    },
    enableSorting: false,
  },
  {
    accessorKey: "provider",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Provider" />
    ),
    cell: ({ row }) => {
      const rowData = row.original.check_metadata?.provider || "N/A";
      const label = providers.find(
        (d) => d.value === rowData
      )?.label
      if (!label) {
        return null
      }
      return (
        <div className="flex items-center">
          <span>{label}</span>
        </div>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.original.check_metadata?.provider)
    },
    enableSorting: false,
  },
]