import os
import urllib.request
import subprocess
import sys

def main():
    # Download ANTLR4 jar
    antlr_version = "4.13.1"
    antlr_jar_url = f"https://www.antlr.org/download/antlr-{antlr_version}-complete.jar"
    antlr_jar_path = os.path.join(os.path.dirname(__file__), f"antlr-{antlr_version}-complete.jar")
    
    print(f"Downloading ANTLR4 {antlr_version}...")
    urllib.request.urlretrieve(antlr_jar_url, antlr_jar_path)
    
    # Create batch script for Windows
    batch_script = os.path.join(os.path.dirname(__file__), "antlr4.bat")
    with open(batch_script, "w") as f:
        f.write(f'@echo off\njava -jar "%~dp0antlr-{antlr_version}-complete.jar" %*')
    
    print("Successfully installed ANTLR4")
    print(f"ANTLR4 jar location: {antlr_jar_path}")
    print(f"ANTLR4 batch script: {batch_script}")
    print("\nAdd the following directory to your PATH:")
    print(os.path.dirname(__file__))

if __name__ == '__main__':
    main() 