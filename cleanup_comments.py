"""Auto-clean comments from all Python scripts."""
import os
import re
from pathlib import Path

def cleanup_comments(file_path):
    """Remove verbose comments, keep minimal comments and docstrings."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.split('\n')
    cleaned = []
    skip_next_block = False
    
    for i, line in enumerate(lines):
        # Keep module docstrings
        if i < 3 and ('"""' in line or "'''" in line):
            cleaned.append(line)
            continue
        
        # Remove section divider comments
        if re.match(r'^#\s*=+', line):
            continue
        
        # Remove obvious inline comments
        obvious_comments = [
            '# Create', '# Load', '# Set', '# Add', '# Train', '# Evaluate',
            '# Tune', '# Calculate', '# Print', '# Save', '# Initialize',
            '# Configuration', '# Results', '# Best', '# Parameters'
        ]
        if any(line.strip().startswith(c) for c in obvious_comments):
            continue
        
       
        if 'print(' in line:
            cleaned.append(line)
            continue
        
        # Keep lines without comments
        if '#' not in line:
            cleaned.append(line)
            continue
        
        # For lines with code + comment, keep if comment is critical
        if '#' in line and not line.strip().startswith('#'):
            code_part = line.split('#')[0]
            comment_part = line.split('#', 1)[1].strip()
            
            # Remove if comment is just restating code
            if len(comment_part) < 30 and not any(k in comment_part for k in ['TODO', 'FIXME', 'NOTE']):
                cleaned.append(code_part.rstrip())
                continue
            
            cleaned.append(line)
            continue
        
        # Keep other meaningful comment lines
        if line.strip().startswith('#') and len(line.strip()) > 2:
            cleaned.append(line)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned))
    
    return len(lines) - len([l for l in cleaned if l.strip() == ''])

if __name__ == '__main__':
    scripts_dirs = [
        'scripts',
        'scripts_v3',
        'scripts_v6_final'
    ]
    
    total_removed = 0
    for dir_name in scripts_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            py_files = list(dir_path.glob('*.py'))
            print(f"\n {dir_name}/ ({len(py_files)} files)")
            for py_file in py_files:
                removed = cleanup_comments(py_file)
                print(f"    {py_file.name}")
                total_removed += removed
    
    print(f"\n Cleanup complete! Removed ~{total_removed} comment lines.")
