export interface Sample {
  documentId: string;
  label: string;
  text: string;
}

const CLEAN_TEXT = `PAYSTUB
Employer: Acme Fixtures LLC
Employee: Jordan Sample
Pay Frequency: biweekly
Pay Period: 2025-01-01 to 2025-01-14
Pay Date: 2025-01-19

Earnings
  Gross Pay (this period): 4200.00
  Deductions (this period): 1000.00
  Net Pay (this period): 3200.00

Year to Date
  YTD Gross: 8400.00
  YTD Net: 6400.00
`;

// Per-period gross inflated to 5600.00 while YTD gross stays at the true 8400.00
// (2 x the true 4200.00). 8400 / 5600 = 1.5, so it no longer reconciles.
const TAMPERED_TEXT = CLEAN_TEXT.replace(
  "Gross Pay (this period): 4200.00",
  "Gross Pay (this period): 5600.00",
);

export const CLEAN_SAMPLE: Sample = {
  documentId: "paystub-clean-sample",
  label: "Clean paystub",
  text: CLEAN_TEXT,
};

export const TAMPERED_SAMPLE: Sample = {
  documentId: "paystub-tampered-sample",
  label: "Tampered paystub (inflated income)",
  text: TAMPERED_TEXT,
};
