import streamlit as st
import os
import sys
import importlib.util
import subprocess
import json
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Python Mini Projects Hub",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dictionary of project descriptions
PROJECT_DESCRIPTIONS = {
    "BoschEBike": {
        "title": "Bosch eBike Analytics System",
        "description": "A sophisticated analytics platform for Bosch eBike systems that helps monitor, analyze, and optimize eBike performance.",
        "main_file": "ebike_analytics.py",
        "requires_direct_run": False,  # Changed to False since we'll handle it in the hub
        "requirements": ["plotly", "pandas", "numpy"]
    },
    "Ascii_Art": {
        "title": "ASCII Art Generator",
        "description": "Convert images into ASCII art with customizable output and support for multiple image formats.",
        "main_file": "ascii_art.py",
        "requires_direct_run": False,
        "requirements": ["Pillow"]
    },
    "TTT_AI": {
        "title": "Tic-Tac-Toe with AI",
        "description": "Play Tic-Tac-Toe against an AI using the Minimax algorithm or against another player.",
        "main_file": "tic_tac_toe.py",
        "requires_direct_run": False,
        "requirements": ["numpy"]
    },
    "Movie_Scraper": {
        "title": "Movie Information Scraper",
        "description": "Search and retrieve detailed movie information from IMDB.",
        "main_file": "movie_scraper.py",
        "requires_direct_run": False,
        "requirements": ["beautifulsoup4", "requests", "pandas"]
    },
    "SpeechToText": {
        "title": "Speech-to-Text Converter",
        "description": "Convert spoken words into text using Google's Speech Recognition.",
        "main_file": "SpeechToTxt.py",
        "requires_direct_run": False,
        "requirements": ["SpeechRecognition"]
    },
    "TextToSpeech": {
        "title": "Text-to-Speech Converter",
        "description": "Convert written text into spoken words with multiple voice options.",
        "main_file": "text_to_speech.py",
        "requires_direct_run": False,
        "requirements": ["gTTS"]
    }
}

def install_package(package_name):
    """Install a Python package using pip"""
    try:
        # Use sys.executable to ensure we use the correct Python interpreter
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--user", package_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Verify installation
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        st.error(f"Error installing {package_name}: {str(e)}")
        return False

def check_requirements(project):
    """Check if all required packages for a project are installed"""
    if "requirements" not in project:
        return []
    
    missing_packages = []
    try:
        # Get list of installed packages using pip
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        installed_packages = {
            pkg["name"].lower(): pkg["version"] 
            for pkg in json.loads(result.stdout)
        }
        
        for package in project["requirements"]:
            package_name = package.lower().split(">=")[0].split("==")[0].strip()
            if package_name not in installed_packages:
                missing_packages.append(package)
    except Exception as e:
        st.error(f"Error checking packages: {str(e)}")
        return project["requirements"]
    
    return missing_packages

def load_project_module(project_dir, main_file):
    """Dynamically load a project's main module"""
    try:
        module_path = os.path.join(os.getcwd(), project_dir, main_file)
        spec = importlib.util.spec_from_file_location(project_dir, module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[project_dir] = module
            spec.loader.exec_module(module)
            return module
        return None
    except Exception as e:
        st.error(f"Error loading {project_dir}: {str(e)}")
        return None

def refresh_environment():
    """Refresh the Python environment after package installation"""
    try:
        importlib.invalidate_caches()
        # Force reload site packages
        importlib.reload(site)
        return True
    except Exception as e:
        st.error(f"Error refreshing environment: {str(e)}")
        return False

def main():
    # Sidebar
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")
    
    # Main content
    st.title("Python Mini Projects Hub 🐍")
    st.markdown("""
    Welcome to the Python Mini Projects Hub! This is a collection of various Python projects 
    demonstrating different aspects of Python programming. Select a project from the sidebar 
    to get started.
    """)
    
    # Get available project directories
    project_dirs = [d for d in os.listdir() if os.path.isdir(d) and d in PROJECT_DESCRIPTIONS]
    
    # Create selection in sidebar
    selected_project = st.sidebar.selectbox(
        "Select a Project",
        ["Home"] + project_dirs,
        format_func=lambda x: "Home" if x == "Home" else PROJECT_DESCRIPTIONS[x]["title"]
    )
    
    if selected_project == "Home":
        # Display project cards in a grid
        col1, col2 = st.columns(2)
        
        for idx, project_dir in enumerate(project_dirs):
            project = PROJECT_DESCRIPTIONS[project_dir]
            with (col1 if idx % 2 == 0 else col2):
                with st.expander(f"📁 {project['title']}", expanded=True):
                    st.markdown(f"**{project['description']}**")
                    if "requirements" in project:
                        st.caption(f"Required packages: {', '.join(project['requirements'])}")
                    if st.button(f"Open {project['title']}", key=f"btn_{project_dir}"):
                        st.session_state["selected_project"] = project_dir
                        st.rerun()
    
    else:
        # Display selected project
        project = PROJECT_DESCRIPTIONS[selected_project]
        st.header(f"📁 {project['title']}")
        st.markdown(f"**{project['description']}**")
        st.markdown("---")
        
        # Check requirements before running
        missing_packages = check_requirements(project)
        if missing_packages:
            st.warning(f"Missing required packages: {', '.join(missing_packages)}")
            if st.button("Install Missing Requirements"):
                success = True
                with st.spinner("Installing required packages..."):
                    for package in missing_packages:
                        if not install_package(package):
                            success = False
                            break
                    
                    if success:
                        # Refresh the environment
                        if refresh_environment():
                            st.success("All requirements installed successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Packages installed but environment refresh failed. Please restart the application.")
                    else:
                        st.error("Failed to install some requirements. Please try installing them manually using pip.")
                return
        
        # Add the project directory to Python path
        project_path = os.path.join(os.getcwd(), selected_project)
        if project_path not in sys.path:
            sys.path.append(project_path)
        
        # Try to load and run the project module
        module = load_project_module(selected_project, project['main_file'])
        if module and hasattr(module, 'main'):
            try:
                # Initialize session state for the project if needed
                if not hasattr(st.session_state, f"{selected_project}_initialized"):
                    setattr(st.session_state, f"{selected_project}_initialized", True)
                
                module.main()
            except Exception as e:
                st.error(f"Error running {selected_project}: {str(e)}")
        else:
            st.error(f"Could not load the {selected_project} module. Please make sure all requirements are installed.")

if __name__ == "__main__":
    main() 