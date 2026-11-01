import importlib
import inspect
import pkgutil
from langchain_core.tools import BaseTool

TOOLS = []
_seen = set()

for module_info in pkgutil.iter_modules(__path__):
    if module_info.name.startswith("_"):
        continue
    module = importlib.import_module(f"{__name__}.{module_info.name}")
    for _, obj in inspect.getmembers(module, lambda o: isinstance(o, BaseTool)):
        if obj.name not in _seen:  # skip duplicates if one file imports another's tool
            _seen.add(obj.name)
            TOOLS.append(obj)
            