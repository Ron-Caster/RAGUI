import pkg_resources
import re
from pathlib import Path

def get_installed_version(package_name):
    """Get the installed version of a package."""
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return None

def parse_requirements(filename):
    """Parse requirements file and return dict of package info."""
    requirements = {}
    with open(filename, 'r') as f:
        current_comment = ""
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                current_comment = line
            elif line:
                # Extract package name and version constraint
                match = re.match(r'^([^>=<]+)([>=<]+.+)?$', line)
                if match:
                    package = match.group(1).strip()
                    requirements[package] = {
                        'constraint': match.group(2) if match.group(2) else '>=',
                        'comment': current_comment
                    }
    return requirements

def update_requirements():
    req_file = Path(__file__).parent / 'requirements.txt'
    if not req_file.exists():
        print("requirements.txt not found!")
        return

    # Parse existing requirements
    requirements = parse_requirements(req_file)
    
    # Check installed versions and prepare new content
    new_content = []
    missing_packages = []
    
    # Add header
    new_content.append("# Updated requirements - Installed versions\n")
    
    current_comment = ""
    for package, info in requirements.items():
        version = get_installed_version(package)
        
        # Handle comment sections
        if info['comment'] and info['comment'] != current_comment:
            current_comment = info['comment']
            new_content.append(f"\n{current_comment}\n")
        
        if version:
            new_content.append(f"{package}>={version}\n")
        else:
            missing_packages.append(package)
    
    # Write updated requirements
    with open(req_file, 'w') as f:
        f.writelines(new_content)
    
    # Print summary
    print("Requirements updated successfully!")
    if missing_packages:
        print("\nWarning: The following packages are in requirements.txt but not installed:")
        for package in missing_packages:
            print(f"- {package}")
        print("\nTo install missing packages, run: pip install -r requirements.txt")

if __name__ == "__main__":
    update_requirements()
