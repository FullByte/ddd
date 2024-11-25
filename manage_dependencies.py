##########################
## Make docs great again #
##########################

import subprocess
import ast
import os
import pkg_resources

# Update pip in the Virtual Environment
def update_pip():
    subprocess.run(["pip", "install", "--upgrade", "pip"])
    print("pip updated to the latest version.")

def scan_code_for_imports(directory="."):
    """Scan all Python files in the directory for imported libraries."""
    imported_modules = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=file_path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    imported_modules.add(alias.name.split('.')[0])
                            elif isinstance(node, ast.ImportFrom):
                                imported_modules.add(node.module.split('.')[0])
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
    return imported_modules


def sync_requirements(required_libraries):
    """Synchronize the libraries in the virtual environment."""
    # Get installed libraries
    installed_libraries = {pkg.key for pkg in pkg_resources.working_set}

    # Libraries to install and uninstall
    to_install = required_libraries - installed_libraries
    to_uninstall = installed_libraries - required_libraries

    # Install missing libraries
    if to_install:
        print("Installing libraries:", to_install)
        subprocess.run(["pip", "install", *to_install])

    # Uninstall unused libraries
    if to_uninstall:
        print("Uninstalling libraries:", to_uninstall)
        subprocess.run(["pip", "uninstall", "-y", *to_uninstall])

def update_libraries():
    """Update all installed libraries."""
    subprocess.run(["pip", "install", "--upgrade", *(pkg.key for pkg in pkg_resources.working_set)])
    print("All libraries updated.")

def generate_requirements_file():
    """Generate a new requirements.txt file."""
    subprocess.run(["pip", "freeze", ">", "requirements.txt"], shell=True)
    print("requirements.txt updated.")


# Run code
update_pip()

required_libraries = scan_code_for_imports()
print("Required libraries:", required_libraries)

sync_requirements(required_libraries)

update_libraries()

generate_requirements_file()


