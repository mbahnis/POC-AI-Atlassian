"""Module IA commun du POC : un seul point d'appel, interchangeable."""

from .engine import ask, extract_json

__all__ = ["ask", "extract_json"]
