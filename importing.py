import re
import glob
import subprocess

packages = set()
for file in glob.glob('*.py'):
    try:
        with open(file, encoding='utf-8', errors='ignore') as f:
            content = f.read()
            imports = re.findall(r'^(?:import|from)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
            packages.update(imports)
    except Exception as e:
        print(f"Warning: Could not read {file}: {e}")

packages = sorted(p for p in packages if not p.startswith('_'))

print(f"Found {len(packages)} unique imports to add:\n")
for package in packages:
    print(f"  - {package}")

print("\nAdding packages...")
for package in packages:
    print(f"\nAdding {package}...")
    subprocess.run(['uv', 'add', package])

print("\nDone!")