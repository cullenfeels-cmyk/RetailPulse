"""
=========================================================
RetailPulse AI Platform
Configuration File
Author : Gulafsha
=========================================================
"""

from pathlib import Path

# ----------------------------------------------------
# Project Information
# ----------------------------------------------------

APP_NAME = "RetailPulse AI Platform"
APP_VERSION = "2.0"
AUTHOR = "Gulafsha"

# ----------------------------------------------------
# Project Paths
# ----------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

# Default Dataset
DATA_FILE = DATA_DIR / "cleaned_data.csv"

# ----------------------------------------------------
# Dashboard Theme
# ----------------------------------------------------

PRIMARY_COLOR = "#4F46E5"
SECONDARY_COLOR = "#0F172A"
SUCCESS_COLOR = "#22C55E"
WARNING_COLOR = "#F59E0B"
DANGER_COLOR = "#EF4444"

# ----------------------------------------------------
# Dashboard Defaults
# ----------------------------------------------------

DEFAULT_FORECAST_DAYS = 30

TOP_PRODUCTS = 10

TOP_CUSTOMERS = 10

TOP_COUNTRIES = 10