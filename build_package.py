"""Build script for Hawkins Agent Framework"""

import os
import subprocess
import shutil

def clean_build_dirs():
    """Clean up build directories"""
    dirs_to_clean = ['dist', 'build', '*.egg-info']
    for dir_name in dirs_to_clean:
        try:
            shutil.rmtree(dir_name)
        except FileNotFoundError:
            pass

def build_package():
    """Build the package"""
    try:
        # Clean previous builds
        clean_build_dirs()
        
        # Install build dependencies
        subprocess.run(['pip', 'install', '--upgrade', 'build', 'twine'], check=True)
        
        # Build the package
        subprocess.run(['python', '-m', 'build'], check=True)
        
        print("Build completed successfully!")
        print("\nTo publish to PyPI, run:")
        print("python -m twine upload dist/*")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    build_package()
