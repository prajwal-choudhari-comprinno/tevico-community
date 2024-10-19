import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export interface Page {

  // The name of the page
  name: string,

  // The title of the page that will be displayed in the browser tab
  pageTitle: string,

  // The header of the page displayed at the page body
  pageHeader?: string,

  // The description of the page
  description?: string
}

interface PageConfig {
  [key: string]: Page
}

export const pageNames = {
  frameworks: 'frameworks',
  browse: 'browse',
  index: 'index'
};

export const pages: PageConfig = {
  [pageNames.frameworks]: {
    name: 'frameworks',
    pageTitle: 'Tevico Report | Frameworks',
    pageHeader: 'Frameworks',
  },
  [pageNames.browse]: {
    name: 'browse',
    pageTitle: 'Tevico Report | Browse Checks',
    pageHeader: 'Browse Checks',
  },
  [pageNames.index]: {
    name: 'index',
    pageTitle: 'Tevico Report | Summary',
    pageHeader: 'Summary',
  }
}
