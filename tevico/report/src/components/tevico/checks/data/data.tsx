export const status = [
  {
    value: "pass",
    label: "Pass",
  },
  {
    value: "fail",
    label: "Fail",
  },
];

export const severity = [
  {
    value: "low",
    label: "Low",
  },
  {
    value: "medium",
    label: "Medium",
  },
  {
    value: "high",
    label: "High",
  },
  {
    value: "critical",
    label: "Critical",
  },
];

export const providers = [
  {
    value: "aws",
    label: "AWS",
  }
];

export const filters = [
  {
    key: 'status',
    title: 'Status',
    options: status
  },
  {
    key: 'severity',
    title: 'Severity',
    options: severity
  },
  {
    key: 'provider',
    title: 'Provider',
    options: providers
  }
];

export const searchBarFilter = {
  key: 'title',
  title: 'Search By Title'

}