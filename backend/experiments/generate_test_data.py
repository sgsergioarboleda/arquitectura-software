#!/usr/bin/env python3
"""
Generate test data for the scheduler agent.

Usage:
    python generate_test_data.py                    # Use default values
    python generate_test_data.py 50 100             # 50 professors, 100 classes
    python generate_test_data.py 50 100 40          # 50 professors, 100 classes, 40 rooms
"""

import pandas as pd
import random
import sys
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Default values (can be overridden via command line)
DEFAULT_PROFESSORS = 102
DEFAULT_CLASSES = 170
DEFAULT_ROOMS = 28

# Randomization seed for reproducibility
RANDOM_SEED = 42

# Output paths
OUTPUT_DIR = "data"
OUTPUT_EXCEL = "input_schedule.xlsx"
OUTPUT_ROOMS = "rooms.txt"

# ============================================================================
# DATA GENERATION LOGIC
# ============================================================================

def generate_professors(n: int) -> list:
    """Generate n professor names (Prof_01, Prof_02, ...)"""
    return [f"Prof_{i+1:02d}" for i in range(n)]

def generate_classes(m: int) -> list:
    """Generate m class names (Clase_001, Clase_002, ...)"""
    # Use 3 digits for classes to support up to 999 classes
    digits = max(3, len(str(m)))
    return [f"Clase_{i+1:0{digits}d}" for i in range(m)]

def generate_rooms(num_rooms: int) -> list:
    """
    Generate room names.
    
    Pattern: 
    - Letters A-Z (cycling if needed)
    - Numbers 101-104 for each letter
    - Example: A101, A102, A103, A104, B101, B102, ...
    """
    rooms = []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    rooms_per_letter = 4  # 101-104
    
    letters_needed = (num_rooms + rooms_per_letter - 1) // rooms_per_letter
    
    for i in range(letters_needed):
        letter = letters[i % len(letters)]
        for num in range(101, 101 + rooms_per_letter):
            if len(rooms) >= num_rooms:
                break
            rooms.append(f"{letter}{num}")
        if len(rooms) >= num_rooms:
            break
    
    return rooms[:num_rooms]

def format_time(h: int) -> str:
    """Format hour as HH:00"""
    return f"{h:02d}:00"

def random_availability() -> str:
    """
    Generate random availability window.
    Start: between 7am and 12pm
    End: between 3pm and 8pm
    Ensures at least 3 hours window
    """
    start = random.randint(7, 12)
    end = random.randint(max(start + 3, 15), 20)
    return f"{format_time(start)}-{format_time(end)}"

def generate_schedule_data(num_professors: int, num_classes: int) -> pd.DataFrame:
    """Generate schedule input data"""
    random.seed(RANDOM_SEED)
    
    # Generate entities
    professors = generate_professors(num_professors)
    classes = generate_classes(num_classes)
    
    # Options
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    groups = [f"G{i}" for i in range(1, 7)]
    
    # Generate rows
    rows = []
    for clase in classes:
        profesor = random.choice(professors)
        dia = random.choice(days)
        grupo = random.choice(groups)
        disponibilidad = random_availability()
        
        rows.append({
            "Clase": clase,
            "Profesor": profesor,
            "Dia de la semana": dia,
            "grupo": grupo,
            "disponibilidad del docente": disponibilidad
        })
    
    return pd.DataFrame(rows)

def save_excel(df: pd.DataFrame, output_path: str):
    """Save DataFrame to Excel file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"✓ Saved Excel: {output_path}")

def save_rooms(rooms: list, output_path: str):
    """Save rooms list to text file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for room in rooms:
            f.write(room + "\n")
    print(f"✓ Saved rooms: {output_path}")

def print_summary(df: pd.DataFrame, rooms: list):
    """Print summary statistics"""
    print("\n" + "="*60)
    print("GENERATED DATA SUMMARY")
    print("="*60)
    
    print(f"\n📊 Classes: {len(df)}")
    print(f"👨‍🏫 Professors: {df['Profesor'].nunique()}")
    print(f"🚪 Rooms: {len(rooms)}")
    print(f"👥 Groups: {df['grupo'].nunique()}")
    print(f"📅 Days: {df['Dia de la semana'].nunique()}")
    
    print(f"\n📈 Professor workload:")
    workload = df['Profesor'].value_counts()
    print(f"   Min: {workload.min()} classes")
    print(f"   Max: {workload.max()} classes")
    print(f"   Avg: {workload.mean():.1f} classes")
    
    print(f"\n📋 Classes per day:")
    for day, count in df['Dia de la semana'].value_counts().sort_index().items():
        print(f"   {day}: {count}")
    
    print(f"\n🏫 Rooms list (showing first 10):")
    for i, room in enumerate(rooms[:10]):
        print(f"   {room}", end="  ")
        if (i + 1) % 5 == 0:
            print()
    if len(rooms) > 10:
        print(f"\n   ... and {len(rooms) - 10} more")
    else:
        print()
    
    print("\n" + "="*60)
    print("\n📄 Sample data (first 5 rows):")
    print(df.head())
    print("\n" + "="*60)

# ============================================================================
# MAIN
# ============================================================================

def main():
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            num_professors = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid number of professors: {sys.argv[1]}")
            sys.exit(1)
    else:
        num_professors = DEFAULT_PROFESSORS
    
    if len(sys.argv) > 2:
        try:
            num_classes = int(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid number of classes: {sys.argv[2]}")
            sys.exit(1)
    else:
        num_classes = DEFAULT_CLASSES
    
    if len(sys.argv) > 3:
        try:
            num_rooms = int(sys.argv[3])
        except ValueError:
            print(f"Error: Invalid number of rooms: {sys.argv[3]}")
            sys.exit(1)
    else:
        num_rooms = DEFAULT_ROOMS
    
    # Validate inputs
    if num_professors < 1:
        print("Error: Number of professors must be at least 1")
        sys.exit(1)
    if num_classes < 1:
        print("Error: Number of classes must be at least 1")
        sys.exit(1)
    if num_rooms < 1:
        print("Error: Number of rooms must be at least 1")
        sys.exit(1)
    
    # Show configuration
    print("="*60)
    print("SCHEDULER TEST DATA GENERATOR")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Professors: {num_professors}")
    print(f"  Classes:    {num_classes}")
    print(f"  Rooms:      {num_rooms}")
    print(f"  Seed:       {RANDOM_SEED}")
    print()
    
    # Generate data
    print("Generating schedule data...")
    df = generate_schedule_data(num_professors, num_classes)
    
    print("Generating rooms...")
    rooms = generate_rooms(num_rooms)
    
    # Save files
    excel_path = os.path.join(OUTPUT_DIR, OUTPUT_EXCEL)
    rooms_path = os.path.join(OUTPUT_DIR, OUTPUT_ROOMS)
    
    save_excel(df, excel_path)
    save_rooms(rooms, rooms_path)
    
    # Print summary
    print_summary(df, rooms)
    
    print(f"\n✅ Done! Files saved to '{OUTPUT_DIR}/' directory")
    print(f"\nTo run the scheduler:")
    print(f"  python agent.py {excel_path} {rooms_path} output.xlsx")

if __name__ == "__main__":
    main()