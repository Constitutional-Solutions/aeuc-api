"""aeuc-api — FSOU-compliant FastAPI REST interface for the AEUC glyph-registry."""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__: str = version("aeuc-api")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .main import app  # noqa: E402

__author__ = "Constitutional-Solutions"
__all__ = ["app", "__version__"]
