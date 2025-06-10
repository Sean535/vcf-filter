# VCF Filter
A command-line Python tool to filter Mutect2-generated VCF files based on JSON-defined criteria, tagging passing variants with `PASS` in the FILTER field. The tool uses the `cyvcf2` library for efficient VCF parsing and streaming, ensuring scalability for large files.

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Design Concept](#design-concept)
- [Testing](#testing)
- [Limitations](#limitations)
- [Maintenance and Extension](#maintenance-and-extension)

## Overview
This tool filters variants in a Mutect2 VCF file by applying user-defined criteria specified in a JSON file. It supports numeric comparisons (e.g., `>=`, `<`) and categorical checks (e.g., `==`, `!=`). Passing variants are tagged with `PASS`, while non-passing variants retain their original FILTER status. The tool is designed for bioinformatics pipelines, emphasizing clean code, robust error handling, and comprehensive documentation.

## Requirements
- **Python**: 3.8 or higher
- **Dependencies**:
  - `cyvcf2`: For efficient VCF parsing
  - `jsonschema`: For JSON validation
- **Input Files**:
  - A valid Mutect2 VCF file
  - A JSON file with filtering criteria follow below struture (`F` for filter name in string, `I` for info name in string, `NUM` for threshold in string)
```JSON
{
  "FILTER": ["!=F1", "==F2", ...],
  "INFO": {
    "I1": ">=NUM1",
    "I2": ">NUM2",
    "I3": "<=NUM3",
    "I4": "<NUM4",
    "I5": "==NUM5",
    "I6": "!=NUM6",
    ...
  },
}
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vcf-filter.git
   cd vcf-filter
   ```
2. Install dependencies:
   ```bash
   pip install cyvcf2 jsonschema
   ```

## Usage
Run the tool from the command line, specifying the input VCF, JSON criteria, and output file:
```bash
python scripts/vcf_filter.py <input.vcf> <criteria.json> [-o <output.vcf>]
```

### Example
Given a JSON file with filtering criteria (`criteria.json`), a vcf file (`SAMPLE_mutect2_raw.vcf`) and output a vcf file (`filtered.vcf`):
```bash
python scripts/vcf_filter.py SAMPLE_mutect2_raw.vcf criteria.json -o filtered.vcf
```

### Output
- A VCF file (default: `filtered_output.vcf`) with variants meeting all criteria tagged as `PASS` in the FILTER column.

## Design Concept
### Core Algorithm
1. **Schema Building**: Parses the VCF header to create a JSON schema, capturing `FILTER`, `INFO`, and `FORMAT` fields with their types (e.g., Float, String).
2. **Criteria Validation**: Validates the JSON criteria against the schema, ensuring fields and operators are valid.
3. **Variant Filtering**: Streams variants using `cyvcf2`, applying criteria to `FILTER` and `INFO` fields. Supports multi-allelic sites by checking if any allele meets numeric criteria.
4. **Output**: Writes filtered variants to a new VCF, setting `PASS` for passing variants.

### Workflow
- **Input Parsing**: Reads VCF and JSON files.
- **Validation**: Ensures VCF header and JSON criteria are valid.
- **Streaming**: Processes variants one at a time to minimize memory usage.
- **Output**: Generates a VCF with updated FILTER tags.

### Handling Multi-Allelic Sites
- For numeric fields (e.g., `TLOD`), the filter passes if *any* allele meets the criteria, as Mutect2 reports per-allele values.
- For categorical fields (e.g., `PON`), *all* allele matches are required.

## Testing
## Test Coverage Descriptions

| Test File                          | Description                                                                 | Expected Result               |
|------------------------------------|-----------------------------------------------------------------------------|-------------------------------|
| valid.json                         | Valid FILTER and INFO criteria.                                             | Pass, output filtered VCF     |
| valid_filter_fail.json             | FILTER condition excludes all records.                                      | Pass, output empty VCF        |
| valid_info_fail.json               | INFO condition excludes all records.                                        | Pass, output empty VCF        |
| malformed.json                     | Malformed JSON (invalid syntax).                                            | Fail, JSON parse error        |
| invalid_schema_filter.json         | FILTER is not a list (invalid schema).                                      | Fail, schema validation error |
| invalid_schema_info.json           | INFO value is not a string (invalid schema).                                | Fail, schema validation error |
| invalid_filter_op.json             | FILTER contains an invalid operator (">=" not supported for FILTER).        | Fail, operator error          |
| invalid_info_num_value.json        | INFO numeric value is not a number.                                         | Fail, value error             |
| invalid_info_num_op.json           | INFO operator is invalid (not recognized).                                  | Fail, operator error          |
| invalid_info_key.json              | INFO key does not exist in VCF records.                                     | Fail, key error               |
| invalid_info_flag_op.json          | INFO flag field with invalid operator.                                      | Fail, operator error          |

**How to run coverage tests:**
```bash
bash run_coverage.sh
```

## Limitations
- **Annotation Support**: Currently supports `FILTER` and `INFO` fields; `FORMAT` fields are not implemented but can be added. Also, annotation libraries included is better than directly parsing input VCF, which might not have the annotation shown in input JSON.
- **Performance**: While optimized for streaming, extremely large VCFs (>10M variants) may require additional optimization (e.g., splitting input file for parallel processing).
- **Flag Fields**: Assumes flag field (e.g., `PON`) presence equates to `True`; other flag behaviors may need customization.

## Maintenance and Extension
### Maintenance
- **Dependencies**: Pin versions in requirements.txt for reproducibility:
```text
cyvcf2==0.30.28
jsonschema==4.23.0
```

### Extension
1. **FORMAT Fields**: Extend `apply_filters` to handle per-sample fields like `AD` or `AF`.
2. **Complex Logic**: Add support for `AND`/`OR` operators in JSON criteria.
3. **Custom Filters**: Allow user-defined Python functions for advanced filtering.
4. **Output Formats**: Support VCF subsets or tabular summaries (e.g., CSV).

### Adding New Features
1. Update `build_json_schema` to include new field types.
2. Extend `validate_condition` for additional field data.
3. Modify `apply_filters` to handle new logic, ensuring backward compatibility.
