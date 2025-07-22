import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from .getFolders import *
from src.getFolders import collect_folders, replicate_folder_structure