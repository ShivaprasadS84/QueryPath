import json
import re
from typing import List, Dict

def generate_aliases(preferred_term: str) -> List[str]:
    """Generate medical aliases for a given preferred term based on actual oncology SNOMED patterns."""
    aliases = [preferred_term]  # Always include the original term first
    
    term_lower = preferred_term.lower()
    
    # Medical abbreviations based on actual data patterns
    abbreviations = {
        'squamous cell carcinoma': ['SCC'],
        'adenocarcinoma': ['adenoCA'],
        'basal cell carcinoma': ['BCC'],
        'transitional cell carcinoma': ['TCC', 'urothelial carcinoma'],
        'renal cell carcinoma': ['RCC'],
        'hepatocellular carcinoma': ['HCC'],
        'acute myeloid leukemia': ['AML', 'acute myelogenous leukemia'],
        'acute lymphoblastic leukemia': ['ALL', 'acute lymphocytic leukemia'],
        'chronic lymphocytic leukemia': ['CLL'],
        'chronic myeloid leukemia': ['CML', 'chronic myelogenous leukemia'],
        'non-hodgkin lymphoma': ['NHL'],
        'hodgkin lymphoma': ['HL', 'Hodgkin disease'],
        'diffuse large b-cell lymphoma': ['DLBCL'],
        'follicular lymphoma': ['FL'],
        'mantle cell lymphoma': ['MCL'],
        'burkitt lymphoma': ['BL'],
        'multiple myeloma': ['MM', 'plasma cell myeloma'],
        'gastrointestinal stromal tumor': ['GIST'],
        'neuroendocrine tumor': ['NET'],
        'small cell lung cancer': ['SCLC'],
        'non-small cell lung cancer': ['NSCLC']
    }
    
    # Apply abbreviations
    for full_term, abbrevs in abbreviations.items():
        if full_term in term_lower:
            for abbrev in abbrevs:
                # Replace the full term with abbreviation
                alias = re.sub(re.escape(full_term), abbrev, preferred_term, flags=re.IGNORECASE)
                if alias != preferred_term and alias not in aliases:
                    aliases.append(alias)
    
    # Generate positional variants based on actual patterns
    
    # Handle "Malignant neoplasm of X" -> "X cancer", "X malignancy", "X malignant neoplasm"
    if 'malignant neoplasm of' in term_lower:
        location_match = re.search(r'malignant neoplasm of (.+)', term_lower)
        if location_match:
            location = location_match.group(1).strip()
            location_title = location.title()
            variants = [
                f"{location_title} cancer",
                f"{location_title} malignancy",
                f"Cancer of {location}"
            ]
            for variant in variants:
                if variant not in aliases and len(variant) < 100:  # Avoid overly long aliases
                    aliases.append(variant)
    
    # Handle "Malignant tumor of X" -> "X cancer", "X tumor"
    if 'malignant tumor of' in term_lower:
        location_match = re.search(r'malignant tumor of (.+)', term_lower)
        if location_match:
            location = location_match.group(1).strip()
            location_title = location.title()
            variants = [
                f"{location_title} cancer",
                f"{location_title} tumor"
            ]
            for variant in variants:
                if variant not in aliases and len(variant) < 100:
                    aliases.append(variant)
    
    # Handle "Primary malignant neoplasm of X" -> "Primary X cancer", "X primary cancer"
    if 'primary malignant neoplasm of' in term_lower:
        location_match = re.search(r'primary malignant neoplasm of (.+)', term_lower)
        if location_match:
            location = location_match.group(1).strip()
            location_title = location.title()
            variants = [
                f"Primary {location} cancer",
                f"{location_title} primary cancer"
            ]
            for variant in variants:
                if variant not in aliases and len(variant) < 100:
                    aliases.append(variant)
    
    # Generate common medical synonyms
    synonyms = {
        'carcinoma': ['cancer', 'CA'],
        'neoplasm': ['tumor', 'cancer', 'malignancy'],
        'tumor': ['neoplasm', 'cancer'],
        'malignant': ['cancerous'],
        'infiltrating': ['invasive'],
        'ductal': ['duct'],
        'lobular': ['lobule']
    }
    
    for original, synonym_list in synonyms.items():
        if original in term_lower:
            for synonym in synonym_list:
                alias = re.sub(r'\b' + re.escape(original) + r'\b', synonym, preferred_term, flags=re.IGNORECASE)
                if alias != preferred_term and alias not in aliases and len(alias) < 120:
                    aliases.append(alias)
    
    # Handle laterality patterns (left/right)
    laterality_patterns = {
        'left female breast': ['L breast', 'left breast'],
        'right female breast': ['R breast', 'right breast'],
        'left lung': ['L lung'],
        'right lung': ['R lung'],
        'left lower limb': ['L lower limb', 'left leg'],
        'right lower limb': ['R lower limb', 'right leg'],
        'left upper limb': ['L upper limb', 'left arm'],
        'right upper limb': ['R upper limb', 'right arm']
    }
    
    for full_term, variants in laterality_patterns.items():
        if full_term in term_lower:
            for variant in variants:
                alias = re.sub(re.escape(full_term), variant, preferred_term, flags=re.IGNORECASE)
                if alias != preferred_term and alias not in aliases:
                    aliases.append(alias)
    
    # Remove redundant modifiers for cleaner aliases
    if ', malignant' in preferred_term:
        clean_version = preferred_term.replace(', malignant', '')
        if clean_version not in aliases:
            aliases.append(clean_version)
    
    # Generate "without primary" variants
    if preferred_term.startswith('Primary '):
        without_primary = preferred_term[8:]  # Remove "Primary "
        if without_primary not in aliases:
            aliases.append(without_primary)
    
    # Limit to 4-5 most relevant aliases
    return aliases[:5]

def process_oncology_data(input_file: str, output_file: str, max_entries: int = 3000):
    """Process oncology SNOMED data and generate aliases."""
    
    print(f"Loading data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Processing first {max_entries} entries...")
    result = {}
    
    for i, entry in enumerate(data[:max_entries]):
        if i % 100 == 0:
            print(f"Processed {i}/{max_entries} entries...")
        
        concept_id = entry['conceptId']
        preferred_term = entry['preferredTerm']
        
        # Generate aliases
        aliases = generate_aliases(preferred_term)
        result[concept_id] = aliases
    
    print(f"Saving results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully processed {len(result)} entries!")
    return result

if __name__ == "__main__":
    input_file = r"c:\Users\320087881\Personal\QueryPath\knowledge_base\oncology_snomed7000.json"
    output_file = r"c:\Users\320087881\Personal\QueryPath\knowledge_base\oncology_snomed_first3000.json"
    
    process_oncology_data(input_file, output_file, max_entries=3000)
