// src/types.ts

import { ComponentType } from "react";

// Define the DropdownFilter interface
export interface DropdownFilter {
  key: string;
  title: string;
  options: {
    value: string;
    label: string;
    icon?: ComponentType<{ className?: string }>;
  }[];
}