import re
import sys
import json
import operator
import argparse
from cyvcf2 import VCF, Writer
from jsonschema import validate, ValidationError

def build_json_schema(vcf_path):
    """Build a JSON schema based on VCF header metadata, capturing all header types."""
    schema = {
        "FILTER": {"type": "array",
            "items": {
                "type": "string"
            }
        },
        "INFO": {},
        "FORMAT": {}
    }

    pattern = re.compile(
        r'##(\w+)=<ID=([^,>]+)'
        r'(?:,Number=([^,>]+))?'
        r'(?:,Type=([^,>]+))?'
    )

    try:
        with open(vcf_path, 'r') as vcf_file:
            for line in vcf_file:
                if re.match(r'^#CHROM', line):
                    break

                match = pattern.search(line)
                if match:
                    Header, ID, Number, Type = match.groups()
                    if Type in {'Float', 'Integer', 'Flag', 'String'}:
                        schema[Header][ID] = {
                            "type": "string",
                            "data_type": Type,
                            "data_size": Number
                        }
    except IOError as e:
        sys.exit(f"Error: Unable to read VCF file {vcf_path}: {e}")
    
    '''
    json_str = json.dumps(schema, indent=4)
    print(json_str)
    '''
    return schema

def validate_criteria(criteria_path, schema):
    """Validate JSON criteria against the schema."""
    try:
        with open(criteria_path, 'r') as f:
            criteria = json.load(f)
    except IOError as e:
        sys.exit(f"Error: Unable to read criteria file {criteria_path}: {e}")
    except json.JSONDecodeError as e:
        sys.exit(f"Error: Invalid JSON format in {criteria_path}: {e}")

    for header in criteria.keys():
        if header in ["INFO", "FORMAT"]:
            for ID in criteria[header]:
                try:
                    validate(instance=criteria[header][ID], schema=schema[header][ID])
                except ValidationError as e:
                    sys.exit(f"Error: Invalid criteria format: {e.message}")
                except KeyError as e:
                    sys.exit(f"Error: Key {ID} is illegal for VCF spec or not mentioned in VCF header.")
        else:
            try:
                validate(instance=criteria[header], schema=schema[header])
            except ValidationError as e:
                sys.exit(f"Error: Invalid criteria format: {e.message}")

    return criteria

def apply_filters(variant, criteria):
    ops = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le
    }

    # --- FILTER field check ---
    if "FILTER" in criteria:
        for filter_cond in criteria["FILTER"]:
            match = re.match(r'^(==|!=)(\S+)$', filter_cond)
            if not match:
                raise ValueError(f"Invalid condition for FILTER: {filter_cond}")
            op_str, filter_val = match.groups()
            
            if not ops[op_str](str(variant.FILTER), filter_val):
                return False

    # --- INFO field checks ---
    if "INFO" in criteria:
        for filter_key, filter_cond in criteria["INFO"].items():
            value = variant.INFO.get(filter_key)
            if value is None:
                return False

            match = re.match(r'^(>=|<=|==|!=|>|<)(\S+)$', filter_cond)
            if not match:
                raise ValueError(f"Invalid condition format for INFO.{filter_key}: {filter_cond}")
            op_str, filter_val = match.groups()
            values = value if isinstance(value, tuple) else (value,)
            
            try:
                # numeric subfields
                if not any(ops[op_str](float(v), float(filter_val)) for v in values):
                    return False
            except ValueError:
                # boolean or string subfields
                if op_str in {'==', '!='}:
                    if not any(ops[op_str](str(v).lower(), filter_val.lower()) for v in values):
                        return False
                else:
                    raise ValueError(f"Invalid string or flag comparison for {filter_key}: {filter_cond}")
    
    return True

def filter_vcf(vcf_path, criteria_path, output_path):
    """Filter VCF file based on JSON criteria and write results to output."""
    print(f'\nvcf file path: {vcf_path}, json file path: {criteria_path}')
    schema = build_json_schema(vcf_path)
    criteria = validate_criteria(criteria_path, schema)

    vcf = VCF(vcf_path)
    out_vcf = Writer(output_path, vcf)

    try:
        for variant in vcf:
            if apply_filters(variant, criteria):
                variant.FILTER = "PASS"
            out_vcf.write_record(variant)
    except Exception as e:
        sys.exit(f"Error processing variants: {e}")
    finally:
        out_vcf.close()
        vcf.close()
    
    print(f"Filtered VCF written to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter Mutect2 VCF using JSON criteria.")
    parser.add_argument("vcf", help="Input VCF file")
    parser.add_argument("criteria", help="JSON filter criteria file")
    parser.add_argument("-o", "--output", default="filtered_output.vcf", help="Output VCF file path")
    args = parser.parse_args()

    filter_vcf(args.vcf, args.criteria, args.output)