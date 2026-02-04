#!/usr/bin/env python3
"""
Azure deployment script using subprocess with proper encoding
"""
import subprocess
import sys
import os

# Set UTF-8 encoding for subprocess
os.environ['PYTHONIOENCODING'] = 'utf-8'

def run_command(cmd, description):
    """Run command with UTF-8 encoding"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode != 0:
            print(f"Warning: Command exited with code {result.returncode}")
            return False
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("Starting Azure deployment...")

    # Step 1: Build image in ACR (no streaming)
    print("\nStep 1: Building Docker image in Azure Container Registry...")
    cmd1 = 'az acr build --registry leadupacr16892 --image leadup-app:latest --no-wait .'
    run_command(cmd1, "Queuing ACR build")

    print("\nWaiting for build to complete (this may take a few minutes)...")
    print("You can check build status in Azure Portal or run: az acr task list-runs --registry leadupacr16892")

    # Step 2: Wait a bit for build
    import time
    time.sleep(10)

    # Step 3: Update container app
    print("\nStep 2: Updating Azure Container App...")
    cmd2 = 'az containerapp update --name leadup-app --resource-group leadup-rg --image leadupacr16892.azurecr.io/leadup-app:latest'
    if run_command(cmd2, "Updating container app"):
        print("\n✓ Deployment initiated successfully!")
        print("\nYour app should be available at:")
        print("https://leadup-app.orangecliff-2bf6ba2e.eastus.azurecontainerapps.io")
    else:
        print("\n✗ Deployment update failed. Please check Azure Portal.")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
