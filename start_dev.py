#!/usr/bin/env python3
"""
Script para ejecutar el sistema completo en modo desarrollo
"""
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def print_output(process, name):
    """Print process output in real-time"""
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            print(f"[{name}] {line.strip()}")

def run_command(command, cwd=None, shell=True):
    """Execute command and return process"""
    print(f"[INFO] Executing: {command}")
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Start thread to print output
        thread = threading.Thread(
            target=print_output,
            args=(process, command),
            daemon=True
        )
        thread.start()
        
        return process
    except Exception as e:
        print(f"[ERROR] Error executing {command}: {e}")
        return None

def main():
    """Main function"""
    print("=== University Management System ===")
    print("=" * 50)
    
    # Verify directories exist
    if not Path("backend").exists() or not Path("frontend").exists():
        print("[ERROR] Must run this script from project root")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start backend
        print("\n[INFO] Starting Backend...")
        backend_process = run_command("python -u run.py", cwd="backend")
        if not backend_process:
            print("[ERROR] Failed to start backend")
            return
        processes.append(("Backend", backend_process))
        
        # Wait for backend to start
        time.sleep(3)
        
        # Start frontend
        print("\n[INFO] Starting Frontend...")
        frontend_process = run_command("npm run dev", cwd="frontend")
        if not frontend_process:
            print("[ERROR] Failed to start frontend")
            backend_process.terminate()
            return
        processes.append(("Frontend", frontend_process))
        
        print("\n[INFO] System started successfully!")
        print("\n[INFO] Available URLs:")
        print("   - Frontend: http://localhost:5173")
        print("   - Backend API: http://localhost:8000")
        print("   - API Docs: http://localhost:8000/docs")
        print("\n[INFO] Press Ctrl+C to stop all services")
        
        # Monitor processes
        while True:
            time.sleep(1)
            for name, process in processes:
                if process.poll() is not None:
                    error_output = process.stdout.read()
                    print(f"\n[ERROR] {name} closed unexpectedly")
                    if error_output:
                        print(f"Error output:\n{error_output}")
                    return
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Stopping services...")
        
    finally:
        # Stop all processes
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"[INFO] {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"[INFO] {name} force stopped")
            except Exception as e:
                print(f"[ERROR] Error stopping {name}: {e}")
        
        print("\n[INFO] Goodbye!")

if __name__ == "__main__":
    main()
