import {
  LineChart,
  TableProperties,
  Frame
} from "lucide-react";

import { Badge } from "@/components/ui/badge";

import { pageNames, pages, type Page } from "@/lib/utils";

export function SideNavigation({ activePage }: { activePage: Page }) {
  const baseClassNames = "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary";
  return (
    <nav className="grid items-start px-2 text-sm font-medium lg:px-4">
      <a
        href="/index.html"
        // className={`${baseClassNames} ${activePage === pages[pageNames.index].name ? "bg-muted" : ""}`}

        // Compare activePage with pages[pageNames.index].name and add "bg-muted" if they are equal
        className={baseClassNames + (activePage.name === pages[pageNames.index].name ? " bg-muted" : "")}
      >
        <LineChart className="h-8 w-4" />
        Summary
      </a>
      <a
        href="/browse/index.html"
        className={baseClassNames + (activePage.name === pages[pageNames.browse].name ? " bg-muted" : "")}
      >
        <TableProperties className="h-8 w-4" />
        Browse Checks
        <Badge className="ml-auto flex h-5 w-5 shrink-0 items-center justify-center rounded-full">
          6
        </Badge>
      </a>
      <a
        href="/frameworks/index.html"
        className={baseClassNames + (activePage.name === pages[pageNames.frameworks].name ? " bg-muted" : "")}
      >
        <Frame className="h-8 w-4" />
        Frameworks
      </a>
    </nav>
  )
};
