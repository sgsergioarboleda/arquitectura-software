# gemini_scheduler_agent_with_rooms.py
"""
Gemini scheduler agent (rooms-aware) with caching support

Input:
 - Excel with columns: Clase, Profesor, Dia de la semana, grupo, disponibilidad del docente
 - TXT file with list of rooms (one room id/name per line)

Behavior:
 - Uses Gemini 3 Pro to propose schedule assignments (day, slot, room) in JSON.
 - Uses Gemini Flash for explanations (cheaper model)
 - Caches Gemini responses to avoid repeated API calls during experimentation
 - Deterministically validates Gemini output
 - Writes output Excel with scheduled and unscheduled sessions
 - If unscheduled sessions exist, requests an explanation + recommendations from Gemini Flash
"""

import os
import re
import json
import sys
import hashlib
import pandas as pd
from datetime import datetime, time, timedelta
from typing import List, Dict, Tuple, Any
from pathlib import Path

# Google GenAI (Gemini)
from google import genai

# ---------------- CONFIG ----------------
GEMINI_MODEL_SCHEDULER = "gemini-3-pro-preview"  # Main model for scheduling
GEMINI_MODEL_EXPLANATION = "gemini-2.0-flash-exp"  # Cheaper model for explanations
SLOT_MINUTES = 60
DAY_START = "08:00"
DAY_END = "18:00"
OUTPUT_SHEET = "Horario"
UNSCHEDULED_SHEET = "No_Pudo_Ser_Asignado"

GEMINI_KEY_ENV = "GEMINI_API_KEY"

# Cache configuration
CACHE_DIR = "cache/LLMresponses"
USE_CACHE = True  # Set to False to bypass cache

# ---------------- Helpers ----------------
SPANISH_DAY_MAP = {
    "LUNES": "L", "L": "L",
    "MARTES": "M", "M": "M",
    "MIERCOLES": "X", "MIÉRCOLES": "X", "X": "X", "MIE": "X",
    "JUEVES": "J", "J": "J",
    "VIERNES": "V", "V": "V", "VIE": "V"
}

time_re_24 = re.compile(r'^([01]?\d|2[0-3]):([0-5]\d)$')
time_re_12 = re.compile(r'^(1[0-2]|0?[1-9])(?::([0-5][0-9]))?\s*(am|pm)?$', re.IGNORECASE)

def normalize_day(d: str) -> str:
    if pd.isna(d): return None
    s = str(d).strip().upper()
    token = s.split()[0]
    return SPANISH_DAY_MAP.get(token)

def parse_time(tstr: str) -> time:
    if tstr is None or (isinstance(tstr, float) and pd.isna(tstr)):
        raise ValueError("Empty time")
    s = str(tstr).strip().lower().replace('.', '')
    m24 = time_re_24.match(s)
    if m24:
        return time(int(m24.group(1)), int(m24.group(2)))
    m12 = time_re_12.match(s)
    if m12:
        hh = int(m12.group(1))
        mm = int(m12.group(2)) if m12.group(2) else 0
        ampm = m12.group(3)
        if ampm:
            if ampm.lower() == 'pm' and hh != 12:
                hh += 12
            if ampm.lower() == 'am' and hh == 12:
                hh = 0
        return time(hh, mm)
    try:
        dt = datetime.fromisoformat(s)
        return dt.time()
    except Exception:
        raise ValueError(f"Cannot parse time: {tstr}")

def parse_availability(av: str) -> Tuple[int,int]:
    if pd.isna(av) or av is None:
        raise ValueError("Availability empty")
    parts = re.split(r'\s*[-–—]\s*', str(av).strip())
    if len(parts) < 2:
        raise ValueError(f"Bad availability format: {av}")
    start = parse_time(parts[0])
    end = parse_time(parts[1])
    return start.hour*60 + start.minute, end.hour*60 + end.minute

def build_slots(start_str: str, end_str: str, slot_minutes: int) -> List[int]:
    start = parse_time(start_str)
    end = parse_time(end_str)
    sm = start.hour*60 + start.minute
    em = end.hour*60 + end.minute
    slots = []
    cur = sm
    while cur + slot_minutes <= em:
        slots.append(cur)
        cur += slot_minutes
    return slots

def slot_to_str(start_min: int, slot_minutes: int) -> str:
    s = (datetime.min + timedelta(minutes=start_min)).strftime("%H:%M")
    e = (datetime.min + timedelta(minutes=start_min+slot_minutes)).strftime("%H:%M")
    return f"{s}-{e}"

# ---------------- Cache utilities ----------------
def ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

def get_cache_key(problem_text: str, model: str) -> str:
    """Generate a unique cache key based on problem content and model"""
    content = f"{model}:{problem_text}"
    hash_obj = hashlib.sha256(content.encode('utf-8'))
    return hash_obj.hexdigest()

def get_cache_path(cache_key: str) -> str:
    """Get the file path for a cache key"""
    return os.path.join(CACHE_DIR, f"gemini_{cache_key}.txt")

def load_from_cache(cache_key: str) -> str:
    """Load cached response if it exists"""
    cache_path = get_cache_path(cache_key)
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def save_to_cache(cache_key: str, response: str):
    """Save response to cache"""
    ensure_cache_dir()
    cache_path = get_cache_path(cache_key)
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(response)

# ---------------- Gemini wrapper ----------------
def init_gemini_client():
    key = os.getenv(GEMINI_KEY_ENV)
    if not key:
        raise RuntimeError(f"{GEMINI_KEY_ENV} env var is not set")
    client = genai.Client(api_key=key)
    return client

def call_gemini_schedule_proposal(client, model: str, problem_text: str, max_output_tokens: int = 4000) -> str:
    """
    Instruct Gemini to reply ONLY with a JSON object.
    Uses caching to avoid repeated API calls during experimentation.
    """
    # Check cache first
    if USE_CACHE:
        cache_key = get_cache_key(problem_text, model)
        cached_response = load_from_cache(cache_key)
        if cached_response:
            print(f"✓ Using cached Gemini response (key: {cache_key[:16]}...)")
            return cached_response
    
    # If not in cache, call Gemini API
    print(f"⟳ Calling Gemini API (model: {model})...")
    
    prompt = (
        "You are an expert deterministic scheduler. Input after --- is a JSON problem with: slot_minutes, "
        "day_start, day_end, rooms (array of room ids), and sessions (array with idx, clase, profesor, dia (L/M/X/J/V or null), grupo, avail_start_m, avail_end_m).\n\n"
        "Output ONLY a JSON object with key 'assignments', an array of objects with fields:\n"
        " - idx (int)\n"
        " - day (L/M/X/J/V or null)\n"
        " - slot (HH:MM-HH:MM or null)\n"
        " - room (one of provided rooms or null)\n"
        " - reason (string or null)\n\n"
        "Constraints: use only provided rooms; each room can host at most one class per slot; professor/group cannot be double-booked; slot must be aligned to slot_minutes grid and within availability. If a session cannot be scheduled, set day, slot and room to null and include a short reason.\n\n"
        "Return valid JSON only.\n\n---\n{problem}\n"
    ).replace("{problem}", problem_text)

    resp = client.models.generate_content(model=model, contents=prompt)
    txt = ""
    if hasattr(resp, "text"):
        txt = resp.text
    else:
        parts = []
        for p in getattr(resp, "parts", []):
            if getattr(p, "text", None):
                parts.append(p.text)
        txt = "".join(parts)
    
    response_text = txt.strip()
    
    # Save to cache
    if USE_CACHE:
        save_to_cache(cache_key, response_text)
        print(f"✓ Cached Gemini response (key: {cache_key[:16]}...)")
    
    return response_text

# ---------------- Gemini justification (cheaper model) ----------------
def ask_gemini_justification(client, scheduled: List[Dict[str,Any]], unscheduled: List[Dict[str,Any]], rooms: List[str]) -> str:
    """
    Use Gemini Flash (cheaper model) to explain scheduling failures and provide recommendations.
    Also uses caching to avoid repeated API calls.
    """
    prompt_content = (
        "Eres un asistente que explica en español por qué falló la asignación de horarios y da recomendaciones prácticas y concretas para resolverlo.\n\n"
        "Voy a darte dos listas: 'scheduled' y 'unscheduled', y la lista de salones disponibles.\n\n"
        "Tu tarea:\n"
        "1. Resume cuántas sesiones se programaron y cuántas no.\n"
        "2. Para cada sesión no programada, explica en lenguaje claro la razón.\n"
        "3. Da 3-6 recomendaciones concretas (por ejemplo: aumentar salones, permitir solapamiento controlado, ampliar disponibilidad de profesores, dividir sesiones, permitir slots de 30 minutos, reubicar grupos) para facilitar que se puedan asignar las sesiones.\n\n"
        f"Salones disponibles:\n{json.dumps(rooms, ensure_ascii=False, indent=2)}\n\n"
        f"Sesiones programadas:\n{json.dumps(scheduled, ensure_ascii=False, indent=2)}\n\n"
        f"Sesiones NO programadas:\n{json.dumps(unscheduled, ensure_ascii=False, indent=2)}\n"
    )
    
    # Check cache first
    if USE_CACHE:
        cache_key = get_cache_key(prompt_content, GEMINI_MODEL_EXPLANATION)
        cached_response = load_from_cache(cache_key)
        if cached_response:
            print(f"✓ Using cached Gemini explanation (key: {cache_key[:16]}...)")
            return cached_response
    
    # If not in cache, call Gemini API
    print(f"⟳ Calling Gemini API for explanation (model: {GEMINI_MODEL_EXPLANATION})...")
    
    resp = client.models.generate_content(
        model=GEMINI_MODEL_EXPLANATION,
        contents=prompt_content
    )
    
    txt = ""
    if hasattr(resp, "text"):
        txt = resp.text
    else:
        parts = []
        for p in getattr(resp, "parts", []):
            if getattr(p, "text", None):
                parts.append(p.text)
        txt = "".join(parts)
    
    response_text = txt.strip()
    
    # Save to cache
    if USE_CACHE:
        save_to_cache(cache_key, response_text)
        print(f"✓ Cached Gemini explanation (key: {cache_key[:16]}...)")
    
    return response_text

# ---------------- Validation (rooms-aware) ----------------
def validate_and_build_output(assignments: List[Dict[str,Any]], sessions_raw: List[Dict[str,Any]], rooms: List[str]) -> Tuple[List[Dict], List[Dict]]:
    days = ["L","M","X","J","V"]
    slots_per_day = build_slots(DAY_START, DAY_END, SLOT_MINUTES)

    occ_prof = {d: {s: None for s in slots_per_day} for d in days}
    occ_group = {d: {s: None for s in slots_per_day} for d in days}
    occ_room = {d: {s: None for s in slots_per_day} for d in days}

    by_idx = {s["idx"]: s for s in sessions_raw}

    scheduled = []
    unscheduled = []

    for a in assignments:
        idx = a.get("idx")
        sess = by_idx.get(idx)
        if sess is None:
            unscheduled.append({"idx": idx, "clase": None, "profesor": None, "dia": None, "grupo": None, "reason": "Unknown idx from model"})
            continue

        day = a.get("day")
        slot = a.get("slot")
        room = a.get("room")
        reason = a.get("reason")

        if day is None or slot is None or room is None:
            unscheduled.append({
                "idx": idx,
                "clase": sess.get("clase"),
                "profesor": sess.get("profesor"),
                "dia": sess.get("dia_raw"),
                "grupo": sess.get("grupo"),
                "reason": reason or "Model did not assign day/slot/room"
            })
            continue

        if day not in days:
            unscheduled.append({
                "idx": idx,
                "clase": sess.get("clase"),
                "profesor": sess.get("profesor"),
                "dia": sess.get("dia_raw"),
                "grupo": sess.get("grupo"),
                "reason": f"Invalid day '{day}' from model"
            })
            continue

        if room not in rooms:
            unscheduled.append({
                "idx": idx, "clase": sess.get("clase"), "profesor": sess.get("profesor"),
                "dia": sess.get("dia_raw"), "grupo": sess.get("grupo"),
                "reason": f"Room '{room}' not in provided rooms"
            })
            continue

        try:
            start_s, end_s = slot.split("-")
            start_dt = datetime.strptime(start_s.strip(), "%H:%M")
            start_min = start_dt.hour * 60 + start_dt.minute
            if start_min not in slots_per_day:
                unscheduled.append({
                    "idx": idx, "clase": sess.get("clase"), "profesor": sess.get("profesor"),
                    "dia": sess.get("dia_raw"), "grupo": sess.get("grupo"),
                    "reason": f"Slot {slot} not aligned with grid"
                })
                continue

            prof_start = sess["avail_start_m"]; prof_end = sess["avail_end_m"]
            if not (start_min >= prof_start and start_min + SLOT_MINUTES <= prof_end):
                unscheduled.append({
                    "idx": idx, "clase": sess.get("clase"), "profesor": sess.get("profesor"),
                    "dia": sess.get("dia_raw"), "grupo": sess.get("grupo"),
                    "reason": f"Slot {slot} outside professor availability ({minutes_to_hm(prof_start)}-{minutes_to_hm(prof_end)})"
                })
                continue

            if occ_prof[day][start_min] is not None:
                unscheduled.append({
                    "idx": idx, "clase": sess.get("clase"), "profesor": sess.get("profesor"),
                    "dia": sess.get("dia_raw"), "grupo": sess.get("grupo"),
                    "reason": f"Professor conflict at slot {slot}"
                })
                continue

            if sess.get("grupo") and occ_group[day][start_min] is not None:
                unscheduled.append({
                    "idx": idx, "clase": sess.get("clase"), "profesor": sess.get("profesor"),
                    "dia": sess.get("dia_raw"), "grupo": sess.get("grupo"),
                    "reason": f"Group conflict at slot {slot}"
                })
                continue

            if occ_room[day][start_min] is None:
                occ_room[day][start_min] = set()
            if room in occ_room[day][start_min]:
                unscheduled.append({
                    "idx": idx, "clase": sess.get("clase"), "profesor": sess.get("profesor"),
                    "dia": sess.get("dia_raw"), "grupo": sess.get("grupo"),
                    "reason": f"Room {room} already used at slot {slot}"
                })
                continue

            occ_prof[day][start_min] = sess["profesor"]
            if sess.get("grupo"):
                occ_group[day][start_min] = sess.get("grupo")
            occ_room[day][start_min].add(room)

            scheduled.append({
                "idx": idx,
                "dia": day,
                "clase": sess.get("clase"),
                "Horario": slot,
                "Profesor": sess.get("profesor"),
                "grupo": sess.get("grupo"),
                "Salon": room
            })

        except Exception as e:
            unscheduled.append({
                "idx": idx, "clase": sess.get("clase"), "profesor": sess.get("profesor"),
                "dia": sess.get("dia_raw"), "grupo": sess.get("grupo"),
                "reason": f"Slot parse/validation error: {e}"
            })

    final_scheduled = []
    extras = []
    by_day_slot = {}
    for s in scheduled:
        key = (s["dia"], s["Horario"])
        by_day_slot.setdefault(key, []).append(s)
    for key, lst in by_day_slot.items():
        if len(lst) <= len(rooms):
            final_scheduled.extend(lst)
        else:
            keep = lst[:len(rooms)]
            dropped = lst[len(rooms):]
            final_scheduled.extend(keep)
            for d in dropped:
                extras.append({
                    "idx": d["idx"],
                    "clase": d["clase"],
                    "profesor": d["Profesor"],
                    "dia": d["dia"],
                    "grupo": d.get("grupo"),
                    "reason": f"More classes ({len(lst)}) than available rooms ({len(rooms)}) at {d['Horario']}"
                })
    unscheduled_final = unscheduled + extras
    return final_scheduled, unscheduled_final

def minutes_to_hm(m: int) -> str:
    return f"{m//60:02d}:{m%60:02d}"

# ---------------- Input building ----------------
def build_problem_json(df: pd.DataFrame, rooms: List[str]) -> Tuple[str, List[Dict]]:
    sessions = []
    for idx, row in df.iterrows():
        dia_raw = row["Dia de la semana"]
        dia = normalize_day(dia_raw)
        try:
            avail_start, avail_end = parse_availability(row["disponibilidad del docente"])
        except Exception:
            parts = re.split(r'[-–—]', str(row["disponibilidad del docente"]))
            if len(parts) >= 2:
                avail_start = parse_time(parts[0].strip()).hour*60 + parse_time(parts[0].strip()).minute
                avail_end = parse_time(parts[1].strip()).hour*60 + parse_time(parts[1].strip()).minute
            else:
                raise
        sessions.append({
            "idx": int(idx),
            "clase": str(row["Clase"]),
            "profesor": str(row["Profesor"]),
            "dia_raw": str(dia_raw),
            "dia": dia,
            "grupo": str(row["grupo"]) if not pd.isna(row["grupo"]) else "",
            "avail_start_m": int(avail_start),
            "avail_end_m": int(avail_end)
        })
    problem = {
        "slot_minutes": SLOT_MINUTES,
        "day_start": DAY_START,
        "day_end": DAY_END,
        "rooms": rooms,
        "sessions": sessions
    }
    return json.dumps(problem, ensure_ascii=False), sessions

# ---------------- IO and outputs ----------------
def read_rooms_txt(path: str) -> List[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Rooms file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        rooms = [line.strip() for line in f if line.strip()]
    if not rooms:
        raise ValueError("Rooms file is empty")
    return rooms

def write_output_excel(scheduled: List[Dict], unscheduled: List[Dict], out_path: str):
    df_sched = pd.DataFrame([{
        "dia de la semana (L-V)": s["dia"],
        "clase": s["clase"],
        "Horario": s["Horario"],
        "Profesor": s["Profesor"],
        "grupo": s.get("grupo",""),
        "Salon": s.get("Salon","")
    } for s in scheduled])
    df_uns = pd.DataFrame([{
        "original_index": u.get("idx"),
        "clase": u.get("clase"),
        "profesor": u.get("profesor"),
        "dia": u.get("dia"),
        "grupo": u.get("grupo"),
        "razon": u.get("reason")
    } for u in unscheduled])
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df_sched.to_excel(writer, sheet_name=OUTPUT_SHEET, index=False)
        if not df_uns.empty:
            df_uns.to_excel(writer, sheet_name=UNSCHEDULED_SHEET, index=False)

# ---------------- Main flow ----------------
def run(input_excel: str, rooms_txt: str, output_excel: str):
    # Init Gemini client (only one needed now)
    gemini_client = init_gemini_client()

    print(f"Reading input excel: {input_excel}")
    df = pd.read_excel(input_excel)
    rooms = read_rooms_txt(rooms_txt)
    print(f"Rooms loaded ({len(rooms)}): {rooms}")

    problem_json, sessions_raw = build_problem_json(df, rooms)

    # Use Gemini Pro for scheduling
    gemini_text = call_gemini_schedule_proposal(gemini_client, GEMINI_MODEL_SCHEDULER, problem_json)

    try:
        parsed = json.loads(gemini_text)
    except Exception:
        m = re.search(r'(\{[\s\S]*\})', gemini_text)
        if m:
            parsed = json.loads(m.group(1))
        else:
            print("Warning: Gemini output not parsable as JSON. Treating as empty assignments.")
            parsed = {"assignments": []}

    assignments = parsed.get("assignments", [])

    scheduled, unscheduled = validate_and_build_output(assignments, sessions_raw, rooms)

    # Use Gemini Flash for explanation if there are unscheduled sessions
    justification = None
    if unscheduled:
        justification = ask_gemini_justification(gemini_client, scheduled, unscheduled, rooms)

    write_output_excel(scheduled, unscheduled, output_excel)

    print(f"Wrote output to {output_excel}")
    print(f"Scheduled: {len(scheduled)}")
    print(f"Unscheduled: {len(unscheduled)}")
    if justification:
        print("\n--- Justification & Recommendations (Gemini Flash) ---\n")
        print(justification)

# ---------------- CLI ----------------
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python gemini_scheduler_agent_with_rooms.py input.xlsx rooms.txt output.xlsx")
        sys.exit(1)
    input_x = sys.argv[1]
    rooms_file = sys.argv[2]
    output_x = sys.argv[3]
    run(input_x, rooms_file, output_x)