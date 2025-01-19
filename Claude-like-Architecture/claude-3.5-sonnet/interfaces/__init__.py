# interfaces/__init__.py
from .controller import BaseController
from .processor import BaseProcessor
from .generator import BaseGenerator

__all__ = ['BaseController', 'BaseProcessor', 'BaseGenerator']