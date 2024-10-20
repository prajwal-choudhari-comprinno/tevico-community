
interface CheckStatusReport {
  total: number;
  passed: number;
  failed: number;
}

interface SeverityReport {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface Report {
  name: string;
  check_status: CheckStatusReport;
  severity: SeverityReport;
}

export interface AnalyticsReport {
  check_status: CheckStatusReport;
  severity: SeverityReport;
  by_services: Report[];
  by_sections: Report[];
  by_severities: Report[];
}
