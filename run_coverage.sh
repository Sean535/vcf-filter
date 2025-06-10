#!/bin/bash

#
mkdir -p tests/outputs

# Copy valid vcf
cp SAMPLE_mutect2_raw.vcf tests/test.vcf

# Generate malformed vcf
echo "##" > tests/malformed.vcf
echo "##FILTER=<ID=PASS,Description=\"All filters passed\"" >> tests/malformed.vcf

# Reset coverage data
coverage erase

# Run test cases
coverage run --source=scripts    -m scripts.vcf_filter tests/test.vcf        tests/valid.json                   -o tests/outputs/valid.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/valid_filter_fail.json       -o tests/outputs/valid_filter_fail.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/valid_info_fail.json         -o tests/outputs/valid_info_fail.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/nonexistent.vcf tests/valid.json                   -o tests/outputs/nonexistent_vcf.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/nonexistent.json             -o tests/outputs/nonexistent_json.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/malformed.vcf   tests/valid.json                   -o tests/outputs/malformed_vcf.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/malformed.json               -o tests/outputs/malformed_json.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/invalid_schema_filter.json   -o tests/outputs/invalid_schema_filter.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/invalid_schema_info.json     -o tests/outputs/invalid_schema_info.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/invalid_filter_op.json       -o tests/outputs/invalid_filter_op.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/invalid_info_key.json        -o tests/outputs/invalid_info_key.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/invalid_info_flag_op.json    -o tests/outputs/invalid_info_flag_op.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/invalid_info_num_op.json     -o tests/outputs/invalid_info_num_op.vcf
coverage run --source=scripts -a -m scripts.vcf_filter tests/test.vcf        tests/invalid_info_num_value.json  -o tests/outputs/invalid_info_num_value.vcf


# Generate coverage report
coverage report -m

# Optional: Generate HTML report
coverage html