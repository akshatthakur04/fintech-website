from fastapi.templating import Jinja2Templates
from pathlib import Path
from config import settings

templates_dir_path = Path(settings.TEMPLATES_DIR).resolve()
templates = Jinja2Templates(directory=templates_dir_path) 