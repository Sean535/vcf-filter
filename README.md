# vcf-filter
A command-line tool to filter Mutect2-generated VCF files based on user-defined criteria in JSON format.

## 📌 Overview
This tool parses a VCF file (produced by GATK Mutect2) and applies filtering rules specified in a JSON file.\
Variants that meet all the criteria are tagged with `PASS` in the FILTER field, while others retain their original FILTER value.

## 🛠 Requirements
- Python 3.8+
- [cyvcf2](https://github.com/brentp/cyvcf2)
- jsonschema

Install dependencies:
```
pip install cyvcf2 jsonschema
```

## 🚀 Usage
- Template:
```
python scripts/vcf_filter.py <input.vcf> <criteria.json> [-o output.vcf]
```
Input:\
input.vcf: A VCF file in Mutect2 format.\
criteria.json: A JSON object with field-based filtering conditions.

- Example:
```
python scripts/vcf_filter.py SAMPLE_mutect2_raw.vcf criteria.json -o filtered_output.vcf
```

## 📂 Output
- A new VCF file where:
Variants passing all filter conditions get PASS in the FILTER field.\
Other variants retain their original FILTER values.

## ⚙ Design
- Filtering Algorithm:
Parse and validate the JSON criteria against the INFO schema extracted from the VCF header.

- For each variant:
Evaluate each filter rule.\
If all are satisfied → FILTER=PASS, otherwise unchanged.\
Write output using streaming (cyvcf2) to support large files.

- Supported Operators:
==, !=, >, >=, <, <=

- Strings must be quoted:
"=="artifact""

- Edge Cases Handled:
Missing fields are treated as non-passing.\
Invalid criteria format raises clear error messages.

## 🧪 Testing
```
pytest tests/test_filter.py
```
You may also generate your own .vcf and .json test data for validation.

## 🧱 Project Structure
```
vcf-filter/
├── scripts/
│   └── vcf_filter.py
├── tests/
│   └── test_filter.py
├── README.md
└── requirements.txt
```

## 📈 Extending the Project
1. Add support for genotype-level filtering.
2. Extend schema validation with more complex types (e.g., array comparisons).
3. Add logging and dry-run features.

## ❗ Limitations
Only INFO and FILTER fields are supported for filtering.\
Multi-allelic handling is simplified: if any alt fails, variant fails.

## 🧾 License
MIT License
