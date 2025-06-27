#!/usr/bin/env python3

import csv
import datetime
import json

from ecologits import EcoLogits
import google.generativeai as genai

ascii_art = """
███████╗ █████╗ ████████╗███████╗██╗████████╗
╚══███╔╝██╔══██╗╚══██╔══╝██╔════╝██║╚══██╔══╝
  ███╔╝ ███████║   ██║   ███████╗██║   ██║   
 ███╔╝  ██╔══██║   ██║   ╚════██║██║   ██║   
███████╗██║  ██║   ██║   ███████║██║   ██║   
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝   ╚═╝   
"""

CONFIG_FILE = "config.json"
CSV_FILE = "gemini_environmental_impact.csv"

def load_api_key():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("API_KEY", "")
    except (FileNotFoundError, json.JSONDecodeError):
        print("Could not load API key ! Please ensure 'config.json' exists and contains a valid API key.")
        return ""
    
def load_model():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("MODEL", "")
    except (FileNotFoundError, json.JSONDecodeError):
        print("Could not load model ! Please ensure 'config.json' exists and contains a valid model name.")
        return ""

def save_impact_to_csv(data):
    fieldnames = list(data.keys())
    try:
        with open(CSV_FILE, "x", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)
    except FileExistsError:
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(data)



print(ascii_art)

api_key = load_api_key()
if not api_key:
    exit(1)
model = load_model()
if not model:
    exit(1)

EcoLogits.init(electricity_mix_zone="FRA")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model)

while True:
    prompt = input("Enter your prompt (or type 'exit' to quit): ").strip()
    if prompt.lower() in {"exit", "quit"}:
        print("Exiting.")
        break

    response = model.generate_content(prompt)
    print("--------------------------------------------------------------------------")
    print(response.text)

    impacts = response.impacts

    data = {
        "Date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "Prompt": prompt,
        "Réponse": response.text,
        "Energy min (kWh)": f"{impacts.energy.value.min}",
        "Energy max (kWh)": f"{impacts.energy.value.max}",
        "GWP min (kgCO2eq)": f"{impacts.gwp.value.min}",
        "GWP max (kgCO2eq)": f"{impacts.gwp.value.max}",
        "ADPe min (kgSbeq)": f"{impacts.adpe.value.min}",
        "ADPe max (kgSbeq)": f"{impacts.adpe.value.max}",
        "PE min (MJ)": f"{impacts.pe.value.min}",
        "PE max (MJ)": f"{impacts.pe.value.max}"
    }

    save_impact_to_csv(data)

    print("--------------------------------------------------------------------------")
    print(f"Environmental impact data saved to: {CSV_FILE}")
    print("--------------------------------------------------------------------------\n")
