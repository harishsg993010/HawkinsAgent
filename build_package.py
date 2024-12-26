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
        subprocess.run(['pip', 'install', '--upgrade', 'build', 'wheel', 'twine'], check=True)

        # Build distribution packages
        print("\nBuilding package...")
        subprocess.run(['python', 'setup.py', 'sdist', 'bdist_wheel'], check=True)

        # If PYPI_TOKEN is available, upload to PyPI
        pypi_token = os.environ.get('PYPI_TOKEN')
        if pypi_token:
            print("\nUploading to PyPI...")
            # Configure twine with token authentication
            os.environ['TWINE_USERNAME'] = '__token__'
            os.environ['TWINE_PASSWORD'] = pypi_token

            # Upload to PyPI using twine
            subprocess.run(['python', '-m', 'twine', 'upload', 'dist/*'], check=True)
            print("Package successfully uploaded to PyPI!")
        else:
            print("\nPackage built successfully!")
            print("To publish to PyPI, ensure PYPI_TOKEN is set in environment")
            print("Then run: python -m twine upload dist/*")

    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    build_package()