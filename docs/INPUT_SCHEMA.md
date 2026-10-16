# Input schema

`input_schema.csv` lists the column names and observed data types in the authors' local analysis-ready exports.

The first public pipeline step validates the presence of these columns, filters to patients with valid positive lactate/BUN/hemoglobin, derives LHR/BHR log2 features, and harmonizes demographic/unit categories exactly as used in the locked modeling cohorts.

No row-level values are included in the repository.
