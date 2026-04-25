"""
Python model 'filas_unimag_clean.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.functions import if_then_else
from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.14.3"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 240,
    "time_step": lambda: 0.0625,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="Minute", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Minute", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    return __data["time"].initial_time()


@component.add(
    name="TIME STEP", units="Minute", comp_type="Constant", comp_subtype="Normal"
)
def time_step():
    return __data["time"].time_step()


@component.add(
    name="SAVEPER",
    units="Minute",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    return __data["time"].saveper()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Aforo_maximo",
    units="Estudiantes",
    comp_type="Constant",
    comp_subtype="Normal",
)
def aforo_maximo():
    return 150


@component.add(
    name="Capacidad_normal",
    units="Estudiantes/Minute",
    comp_type="Constant",
    comp_subtype="Normal",
)
def capacidad_normal():
    return 6


@component.add(
    name="Entrada_estudiantes",
    units="Estudiantes/Minute",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"estudiantes_en_la_fila": 1, "aforo_maximo": 1},
)
def entrada_estudiantes():
    return if_then_else(
        estudiantes_en_la_fila() < aforo_maximo(), lambda: 10, lambda: 0
    )


@component.add(
    name="Estado_sistema",
    units="dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"reposicion_activa": 1},
)
def estado_sistema():
    return if_then_else(reposicion_activa() > 0, lambda: 0, lambda: 1)


@component.add(
    name="Estudiantes en la fila",
    units="Estudiantes",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_estudiantes_en_la_fila": 1},
    other_deps={
        "_integ_estudiantes_en_la_fila": {
            "initial": {"estudiantes_inicial": 1},
            "step": {"entrada_estudiantes": 1, "salida_estudiantes": 1},
        }
    },
)
def estudiantes_en_la_fila():
    return _integ_estudiantes_en_la_fila()


_integ_estudiantes_en_la_fila = Integ(
    lambda: entrada_estudiantes() - salida_estudiantes(),
    lambda: estudiantes_inicial(),
    "_integ_estudiantes_en_la_fila",
)


@component.add(
    name="Estudiantes_inicial",
    units="Estudiantes",
    comp_type="Constant",
    comp_subtype="Normal",
)
def estudiantes_inicial():
    return 5


@component.add(
    name="Llegada_comida_lote",
    units="Platos_comida/Minute",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"reposicion_activa": 1, "stock_inicial": 1, "tiempo_reposicion": 1},
)
def llegada_comida_lote():
    return if_then_else(
        reposicion_activa() > 0,
        lambda: stock_inicial() / tiempo_reposicion(),
        lambda: 0,
    )


@component.add(
    name="Reposicion_activa",
    units="dmnl",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_reposicion_activa": 1},
    other_deps={
        "_integ_reposicion_activa": {
            "initial": {},
            "step": {"tasa_entrada_estado": 1, "tasa_salida_estado": 1},
        }
    },
)
def reposicion_activa():
    return _integ_reposicion_activa()


_integ_reposicion_activa = Integ(
    lambda: tasa_entrada_estado() - tasa_salida_estado(),
    lambda: 0,
    "_integ_reposicion_activa",
)


@component.add(
    name="Tasa_Entrada_Estado",
    units="1/Minute",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"stock_comida": 1, "reposicion_activa": 1, "time_step": 1},
)
def tasa_entrada_estado():
    return if_then_else(
        np.logical_and(stock_comida() <= 0, reposicion_activa() <= 0),
        lambda: 1 / time_step(),
        lambda: 0,
    )


@component.add(
    name="Tasa_Salida_Estado",
    units="1/Minute",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"reposicion_activa": 1, "tiempo_reposicion": 1},
)
def tasa_salida_estado():
    return if_then_else(
        reposicion_activa() > 0, lambda: 1 / tiempo_reposicion(), lambda: 0
    )


@component.add(
    name="Salida_estudiantes",
    units="Estudiantes/Minute",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "estado_sistema": 1,
        "stock_comida": 1,
        "estudiantes_en_la_fila": 1,
        "time_step": 1,
        "capacidad_normal": 1,
    },
)
def salida_estudiantes():
    return if_then_else(
        np.logical_and(estado_sistema() == 1, stock_comida() > 0),
        lambda: float(
            np.minimum(capacidad_normal(), estudiantes_en_la_fila() / time_step())
        ),
        lambda: 0,
    )


@component.add(
    name="Stock_comida",
    units="Platos_comida",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_stock_comida": 1},
    other_deps={
        "_integ_stock_comida": {
            "initial": {"stock_inicial": 1},
            "step": {"llegada_comida_lote": 1, "salida_estudiantes": 1},
        }
    },
)
def stock_comida():
    return _integ_stock_comida()


_integ_stock_comida = Integ(
    lambda: llegada_comida_lote() - salida_estudiantes(),
    lambda: stock_inicial(),
    "_integ_stock_comida",
)


@component.add(
    name="Stock_inicial",
    units="Platos_comida",
    comp_type="Constant",
    comp_subtype="Normal",
)
def stock_inicial():
    return 50


@component.add(
    name="Tiempo_reposicion",
    units="Minute",
    comp_type="Constant",
    comp_subtype="Normal",
)
def tiempo_reposicion():
    return 10
