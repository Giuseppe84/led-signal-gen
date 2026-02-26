import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_app():
    """Run the FastAPI application"""
    print("Starting the application...")
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    # Change to the workspace directory
    os.chdir("/workspace")
    
    # Install requirements if not already installed
    try:
        import fastapi
        import uvicorn
        import PIL
        import trimesh
        print("Dependencies already installed.")
    except ImportError:
        install_requirements()
    
    # Run the application
    run_app()