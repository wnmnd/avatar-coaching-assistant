"""
Setup script for Avatar Success Coach
"""

import os
import subprocess
import sys

def create_secrets_file():
    """Create the secrets.toml file if it doesn't exist"""
    secrets_dir = ".streamlit"
    secrets_file = os.path.join(secrets_dir, "secrets.toml")
    
    # Create directory if it doesn't exist
    if not os.path.exists(secrets_dir):
        os.makedirs(secrets_dir)
        print(f"✅ Created {secrets_dir} directory")
    
    # Create secrets file if it doesn't exist
    if not os.path.exists(secrets_file):
        secrets_content = '''# Add your Gemini API key here
# Get it from: https://makersuite.google.com/app/apikey

GEMINI_API_KEY = "your_gemini_api_key_here"

# Optional: Add other API keys if you want to use premium services later
# ELEVENLABS_API_KEY = "your_elevenlabs_key_here"
# HEYGEN_API_KEY = "your_heygen_key_here"
'''
        
        with open(secrets_file, 'w') as f:
            f.write(secrets_content)
        print(f"✅ Created {secrets_file}")
        print("⚠️  Don't forget to add your actual Gemini API key!")
    else:
        print(f"📁 {secrets_file} already exists")

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor} is compatible")
        return True

def main():
    """Main setup function"""
    print("🎯 Avatar Success Coach Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create secrets file
    create_secrets_file()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
    print("2. Edit .streamlit/secrets.toml and add your API key")
    print("3. Run: streamlit run main.py")
    print("4. Open your browser to http://localhost:8501")
    print("\nHappy coaching! 🚀")

if __name__ == "__main__":
    main()
