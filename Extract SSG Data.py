#%%
import xml.etree.ElementTree as ET
import pandas as pd

# Define the namespace
ns = {'xccdf': 'http://checklists.nist.gov/xccdf/1.2'}

# Function to recursively find all 'group' elements and their nested 'rule' elements
def find_groups_and_rules(element, parent_titles, result):
    if element.tag.endswith('Group'):
        title_element = element.find('xccdf:title', ns)
        current_title = title_element.text.strip() if title_element is not None else 'No Title'
        
        # Find all 'rule' elements under the current 'group'
        rules = element.findall('xccdf:Rule', ns)
        for rule in rules:
            rule_title_element = rule.find('xccdf:title', ns)
            rule_title = rule_title_element.text.strip() if rule_title_element is not None else 'No Title'
            rule_id = rule.attrib.get('id', 'No ID')
            
            # Find <xccdf-1.2:ident> element under the current 'rule'
            ident_element = rule.find('xccdf:ident[@system="https://ncp.nist.gov/cce"]', ns)
            ident_value = ident_element.text.strip() if ident_element is not None else 'No Ident'
            
            # Find up to 5 <xccdf-1.2:reference> elements with href="https://www.cyber.gov.au/acsc/view-all-content/ism" under the current 'rule'
            references = rule.findall('xccdf:reference[@href="https://www.cyber.gov.au/acsc/view-all-content/ism"]', ns)[:15]  # Limit to 15 references max in doco being used is 14, change if needed
            ism_controls = []
            for idx, ref in enumerate(references, start=1):
                text = ref.text.strip() if ref.text else 'No Text'
                ism_controls.append(f"ISM Control {idx}: {text}")
            
            # Append the 'group' title, 'rule' title, 'rule' id, 'ident' value, and 'ISM Control' columns to the result
            result.append({
                'Group Title': current_title,
                'Rule Title': rule_title,
                'Rule ID': rule_id,
                'Ident Value': ident_value,
                **{f'ISM Control {idx}': control for idx, control in enumerate(ism_controls, start=1)},
                'Parent 1': parent_titles[0] if len(parent_titles) > 0 else '',
                'Parent 2': parent_titles[1] if len(parent_titles) > 1 else '',
                'Parent 3': parent_titles[2] if len(parent_titles) > 2 else '',
                'Parent 4': parent_titles[3] if len(parent_titles) > 3 else '',
                'Parent 5': parent_titles[4] if len(parent_titles) > 4 else ''
            })
        
        parent_titles.append(current_title)
        
        # Recursively find child elements (both groups and rules)
        for child in element:
            find_groups_and_rules(child, parent_titles, result)
        
        parent_titles.pop()
    
    else:
        # Continue recursively searching for 'group' and 'rule' elements
        for child in element:
            find_groups_and_rules(child, parent_titles, result)

# Parse the XML file
tree = ET.parse('scap-security-guide-0.1.72-ssg-rhel8-ds.xml')
root = tree.getroot()

# List to hold all 'group' elements, their nested 'rule' elements, 'ident' values, 'ISM Control' references, and parent titles
result = []

# Start the recursive search from the root element
find_groups_and_rules(root, [], result)

# Create a DataFrame and save it to an Excel file
df = pd.DataFrame(result)
df.to_excel('groups_rules_ident_specific_references_with_parentslklkl.xlsx', index=False)

print(f"Found {len(result)} group and rule elements with 'ident' values and specific 'ISM Control' references. Titles, rule titles, 'ident' values, specific 'ISM Control' references, and their parent titles have been saved to groups_rules_ident_specific_references_with_parents.xlsx.")
# %%
