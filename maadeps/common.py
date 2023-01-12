import os
from .host_triplet import detect_host_triplet
import pathlib

host_triplet = detect_host_triplet()
resdir = os.path.abspath(os.path.dirname(__file__))
basedir = str(pathlib.PurePath(resdir).parent)
