# -*- coding: utf-8 -*-
"""
21-11-2022

@author: PAN

Codigo creado cons^erando la norma ISO 52016-1 y validado segun ASHRAE 140 casos base 600 y 900.


"""
import time
from multiprocessing import Pool, cpu_count

from .energy_balance import EnergyBalance
from .output_processor import OutputProcessor
from .sanitize_variables import sanitize_variables
from .utils import len_pared, locate_params
from .vector_processor import VectorProcessor

from src.utils.logging import logger

def processing(callback, *variables):
    with Pool(cpu_count()) as pool:
        pool.map(callback, variables)
class Calculator:
    def __init__(self,input_path:str):
        logger.info("Iniciando calculos")
        self.input_path = input_path
    async def run(self,project_id:str,output_path:str):
        path = self.input_path
        start_time = time.time()
        variables = await sanitize_variables(path)
        lenpared = len_pared(variables.areas)
        params = await locate_params(variables.T, variables.cp, lenpared)
        matches = {'HR': None, 'CT': None, 'FL': None}
        vector_processor = VectorProcessor(matches, variables)
        area, temperaturapared, ordenfinal, Atot = vector_processor.order()
        nodos = await vector_processor.create_vectors(params)
    
        rt, kp, hpl, kpl, hi, he, c_interior,hp = await vector_processor.calc_resistances_coefficients(params, variables, ordenfinal,
                                                                                              temperaturapared)
        calculator_engine = EnergyBalance(variables, params, area, kpl)
        output_calculations = await calculator_engine.calculate(ordenfinal, hi, hpl, he, Atot)
    
        output_name=project_id+".output"
        output_processor = OutputProcessor(output_name,output_calculations, variables, params, ordenfinal, nodos, c_interior)
        output_processor.set_output_path(output_path)
        output_processor.process(params.Informes,hp,hi,hpl,kpl)
    
        end_time = time.time()
        print(f"Tiempo invertido: {end_time - start_time:.2f} segundos")
