interface RemediationCode {
  cli: string | null;
  native_iac: string | null;
  other: string | null;
  terraform: string | null;
}

interface RemediationRecommendation {
  text: string;
  url: string;
}

interface Remediation {
  code: RemediationCode;
  recommendation: RemediationRecommendation;
}

export enum Severity {
  critical = 'critical',
  high = 'high',
  medium = 'medium',
  low = 'low',
}

interface CheckMetadata {
  provider: string;
  check_id: string;
  check_title: string;
  check_aliases: string[];
  check_type: string[];
  service_name: string;
  sub_service_name: string;
  resource_id_template: string;
  severity: Severity;
  resource_type: string;
  risk: string;
  related_url: string;
  remediation: Remediation;
  categories: string[];
  depends_on: string[];
  related_to: string[];
  notes: string;
  description: string;
  success_message: string | null;
  failure_message: string | null;
}

interface ResourceIdsStatus {
  [key: string]: boolean;
}

interface ReportMetadata {
  findings?: {
    resource_arn: string;
    resource_id: string;
    resource_tags: object;
    status: string;
    status_extended: string;
  }[];
  error?: string;
}

export interface CheckReport {
  passed: boolean;
  name: string;
  check_metadata: CheckMetadata;
  dimensions: string[];
  profile_name: string;
  resource_ids_status: ResourceIdsStatus;
  report_metadata: ReportMetadata | null;
  created_on: string;
}
