import { columns } from "./columns";
import { DataTable } from "@/components/tevico/data-table/data-table";
import { filters, searchBarFilter } from './data/data'
import CheckReports from "@/data/check_reports.json";
import { CheckReport } from "@/components/tevico/types/checkTypes";

const checkReport = CheckReports as unknown as CheckReport[];

export default function ChecksPage() {
  return (
    <div>
      <DataTable data={checkReport} columns={columns} dropdownFilter={filters} searchBarFilter={searchBarFilter} />
    </div>
  );
}