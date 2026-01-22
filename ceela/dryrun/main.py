from analisis_resultados import calcular_demanda_refrigeracion_calefaccion, calcular_horas_disconfort
from ejecutable_iso_prueba import ejecutable_iso

ejecutable_iso(1,"Datos.xlsx","./output")
calcular_demanda_refrigeracion_calefaccion("./output/1.output_simple.txt")
calcular_horas_disconfort("./output/1.output_simple.txt")