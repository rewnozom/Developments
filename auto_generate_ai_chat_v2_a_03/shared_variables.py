from tkinter import StringVar, DoubleVar, IntVar

_model_var = None
_temperature_var = None
_max_tokens_var = None
_system_prompt_var = None

def get_model_var():
    global _model_var
    if _model_var is None:
        _model_var = StringVar()
    return _model_var

def get_temperature_var():
    global _temperature_var
    if _temperature_var is None:
        _temperature_var = DoubleVar()
    return _temperature_var

def get_max_tokens_var():
    global _max_tokens_var
    if _max_tokens_var is None:
        _max_tokens_var = IntVar()
    return _max_tokens_var

def get_system_prompt_var():
    global _system_prompt_var
    if _system_prompt_var is None:
        _system_prompt_var = StringVar()
    return _system_prompt_var