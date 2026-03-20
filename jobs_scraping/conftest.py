import sys
import os

scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
scrapers_dir = os.path.join(scripts_dir, "scrapers")

sys.path.insert(0, scripts_dir)
sys.path.insert(0, scrapers_dir)
