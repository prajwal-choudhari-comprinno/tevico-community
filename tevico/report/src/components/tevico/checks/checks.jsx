import { columns } from "./columns";
import { DataTable } from "@/components/tevico/data-table/data-table";
import { data, filters, searchBarFilter } from  './data/data'

export default function ChecksPage() {
  // Log data and columns for debugging
  // console.log("Data:", data);
  // console.log("Columns:", columns);

  return (
    <div>
      <DataTable data={data} columns={columns} dropdownFilter = {filters} searchBarFilter = {searchBarFilter} />
    </div>
  );
}


// // import { promises as fs } from "fs";
// // import path from "path";
// // import { z } from "zod";

// import { columns } from "@/components/tevico/data-table/columns";
// import { DataTable } from "@/components/tevico/data-table/data-table";
// // import { taskSchema } from "./data/schema";

// // // Simulate a database read for tasks.
// // async function getChecks() {
// //   const data = await fs.readFile(
// //     path.join(process.cwd(), "src/pages/checks/data/tasks.json"),
// //     "utf-8" // Read file as UTF-8
// //   );
// //   const tasks = JSON.parse(data.toString());
// //   return z.array(taskSchema).parse(tasks);
// // }

// const data1 =  [
// {
//     "id": "TASK-7839",
//     "title": "We need to bypass the neural TCP card!",
//     "status": "todo",
//     "label": "bug",
//     "priority": "high"
//   },
// ];

// export default function ChecksPage() {
//     //   const tasks = await getChecks(); // Await the data fetching here
//     return (
//         <>
//             <div className="md:hidden">
//                 <DataTable data={data1} columns={columns} />
//             </div>
//         </>
//     );
// }
