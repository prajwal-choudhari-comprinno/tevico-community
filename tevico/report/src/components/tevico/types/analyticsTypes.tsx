interface CheckStatus {
  total: number;
  passed: number;
  failed: number;
}

interface Severity {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

interface Service {
  name: string;
  check_status: CheckStatus;
  severity: Severity;
}

interface Section {
  name: string;
  check_status: CheckStatus;
  severity: Severity;
}

export interface AnalyticsReport {
  check_status: CheckStatus;
  severity: Severity;
  by_services: Service[];
  by_sections: Section[];
}
