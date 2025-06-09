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
This tool filters variants in a Mutect2 VCF file by applying user-defined criteria specified in a JSON file. It supports numeric comparisons (e.g., `>=`, `<`) and categorical checks (e.g., `==`, `!=`) for fields like `TLOD`, `DP`, and `FILTER`. Passing variants are tagged with `PASS`, while non-passing variants retain their original FILTER status. The tool is designed for bioinformatics pipelines, emphasizing clean code, robust error handling, and comprehensive documentation.

## Requirements
- **Python**: 3.8 or higher
- **Dependencies**:
  - `cyvcf2`: For efficient VCF parsing
  - `jsonschema`: For JSON validation
- **Input Files**:
  - A valid Mutect2 VCF file
  - A JSON file with filtering criteria (e.g., `{"INFO": {"TLOD": ">=200", "DP": ">=20"}, "FILTER": ["!=artifact"]}`)

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
- For categorical fields (e.g., `PON`), exact matches are required.

## Testing
### Validation Approach
1. **Unit Tests**:
   - Test schema building with a sample VCF header.
   - Validate JSON criteria parsing and error handling for invalid operators/values.
   - Check filter application on synthetic variants with known outcomes.
2. **Integration Tests**:
   - Use the provided `SAMPLE_mutect2_raw.vcf` with `criteria.json`.
   - Expected: Variants with `TLOD >= 200`, `DP >= 20`, and `PON` flag pass (e.g., chr1:11130589, chr1:11228701).
   - Non-passing variants (e.g., chr1:119510717 with `TLOD=3.09`) retain original FILTER.
3. **Edge Cases**:
   - Test empty VCF files, missing fields, and malformed JSON.
   - Verify multi-allelic sites (e.g., chr1:200624913) handle multiple `TLOD` values correctly.

### Test Dataset
- **Provided**: `SAMPLE_mutect2_raw.vcf` (contains 100+ variants, including multi-allelic sites and PON flags).
- **Synthetic**: Created a small VCF with 10 variants, covering:
  - High/low `TLOD` and `DP`.
  - Presence/absence of `PON`.
  - Multi-allelic sites with mixed passing/failing alleles.
- **Validation**: Manually inspected output VCF to confirm `PASS` tags align with criteria.

### Running Tests
1. Place test files in a `tests/` directory.
2. Run:
   ```bash
   python scripts/vcf_filter.py tests/test.vcf tests/test_criteria.json -o tests/test_output.vcf
   ```
3. Compare `test_output.vcf` with expected results using `diff` or a VCF comparison tool.

## Limitations
- **Field Support**: Currently supports `FILTER` and `INFO` fields; `FORMAT` fields are not implemented but can be added.
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
