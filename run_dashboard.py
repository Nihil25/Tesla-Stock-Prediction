#!/usr/bin/env python3
"""
Tesla Stock Prediction Dashboard Runner
======================================

This script runs the Tesla stock prediction dashboard with proper setup and error handling.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly',
        'yfinance',
        'scikit-learn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("\n📦 Installing missing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_dashboard():
    """Run the Streamlit dashboard"""
    print("\n🚀 Starting Tesla Stock Prediction Dashboard...")
    print("📊 Dashboard will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Run the dashboard
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

def main():
    """Main function to setup and run the dashboard"""
    print("🚗 Tesla Stock Prediction Dashboard")
    print("=" * 40)
    
    # Check if dashboard.py exists
    if not Path("dashboard.py").exists():
        print("❌ dashboard.py not found in current directory")
        print("Please make sure you're in the correct directory")
        return
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        install_choice = input("Would you like to install missing dependencies? (y/n): ").lower()
        
        if install_choice in ['y', 'yes']:
            if not install_dependencies():
                print("❌ Failed to install dependencies. Please install manually:")
                print("pip install -r requirements.txt")
                return
        else:
            print("❌ Cannot run dashboard without required dependencies")
            return
    
    # Run the dashboard
    run_dashboard()

if __name__ == "__main__":
    main()