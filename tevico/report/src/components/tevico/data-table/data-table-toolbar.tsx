"use client"

import { Cross2Icon } from "@radix-ui/react-icons"
import { Table } from "@tanstack/react-table"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { DataTableViewOptions } from "./data-table-view-options"
import { DataTableFacetedFilter } from "./data-table-faceted-filter"
import { DropdownFilter, SearchBarFilter } from "./types"

interface DataTableToolbarProps<TData> {
  table: Table<TData>,
  dropdownFilter: DropdownFilter[],
  searchBarFilter: SearchBarFilter
}

export function DataTableToolbar<TData>({
  table,
  dropdownFilter,
  searchBarFilter
}: DataTableToolbarProps<TData>) {
  const isFiltered = table.getState().columnFilters.length > 0;


  return (
    <div className="flex items-center justify-between">
      <div className="flex flex-1 items-center space-x-2">
        <Input
          placeholder={searchBarFilter.title}
          value={(table.getColumn(searchBarFilter.key)?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn(searchBarFilter.key)?.setFilterValue(event.target.value)
          }
          className="h-8 w-[150px] lg:w-[250px]"
        />
        {/* Render dropdown filters dynamically */}
        {dropdownFilter.map(({ key, title, options }) => (
          table.getColumn(key) && (
            <DataTableFacetedFilter
              key={key}
              column={table.getColumn(key)}
              title={title}
              options={options}
            />
          )
        ))}

        {isFiltered && (
          <Button
            variant="ghost"
            onClick={() => table.resetColumnFilters()}
            className="h-8 px-2 lg:px-3"
          >
            Reset
            <Cross2Icon className="ml-2 h-4 w-4" />
          </Button>
        )}
      </div>
      <DataTableViewOptions table={table} />
    </div>
  )
}
