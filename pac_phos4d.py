#-*- coding: utf-8 -*-
'''
TEST DE LIBRERIAS kUFFLINGS Y PLOTLY

Autores: 
    Ing. Emanuel R. Schumacher
    PhD. Juan Manuel Monteoliva
    
Fecha inicio: -

'''

###### LIBRERÍAS ######
from datetime import datetime
import pandas as pd
import numpy as np
import plotly
import matplotlib.pyplot as plt
import os
import glob
import configparser
from sys import exit
from sys import getsizeof
#import plotly.plotly as py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import configparser

# RUTA DE ARCHIVOS A PROCESAR

filesPath = './'
cnf_path = './pac_phos4d_config.cfg'

filesPathData = ''
filesPathSaveCSV = './'

hour_start = 0
hour_end = 0
month_start = 0
month_end = 0
cdiSensorFraction = 0.0

# CDI  - Characteristic Daylight Illuminance and sCDI
'''
Esta métrica proporciona una interpretación inversa al DA. Ésta
no representa un porcentaje de tiempo correspondiente a una iluminancia objetivo (por ejemplo,
200 lux), sino una iluminancia de tarea (0lx, 50lx, 100lx, 200lx, 300lx, 500lx, 750lx, 1000lx,
2000lx) correspondiente al porcentaje de tiempo ocupado
'''
cdiPorcentajeSensores = 0.5 # fraction of sensor to consider for analysis CDI
scdiPorcentajeSensores = cdiPorcentajeSensores # fraction of sensor to consider for analysis sCDI
cdiSetpoint = 300

#Return hours as Ints
def get_hour_from_header_int(cabecera):
    #parametros = list(cabecera)
    parametros = cabecera.split()
    #print(f"La lista de parametros es: {parametros}\n")
    #print(f"La hora es {parametros[7]}")
    #return parametros[7]
    if parametros[2]=="1)":
        return 0
    elif parametros[2]=="2)":
        return 1
    elif parametros[2]=="3)":
        return 2
    elif parametros[2]=="4)":
        return 3
    elif parametros[2]=="5)":
        return 4
    elif parametros[2]=="6)":
        return 5
    elif parametros[2]=="7)":
        return 6
    elif parametros[2]=="8)":
        return 7
    elif parametros[2]=="9)":
        return 8
    elif parametros[2]=="10)":
        return 9
    elif parametros[2]=="11)":
        return 10
    elif parametros[2]=="12)":
        return 11
    else:
        return "Index Error"
        #return "NONE"

#Return month as Ints
def get_month_from_header_int(cabecera):
    #parametros = list(cabecera)   
    #return parametros[1]
    parametros = cabecera.split()
    if parametros[0]=="(1,":
        return 0
        #return "january"
    elif parametros[0]=="(2,":
        return 1
        #return "february"
    elif parametros[0]=="(3,":
        return 2
        #return "march"
    elif parametros[0]=="(4,":
        return 3
        #return "april"
    elif parametros[0]=="(5,":
        return 4
        #return "may"
    elif parametros[0]=="(6,":
        return 5
        #return "june"
    elif parametros[0]=="(7,":
        return 6
        #return "july"
    elif parametros[0]=="(8,":
        return 7
        #return "august"
    elif parametros[0]=="(9,":
        return 8
        #return "september"
    elif parametros[0]=="(10,":
        return 9
        #return "october"
    elif parametros[0]=="(11,":
        return 10
        #return "november"
    elif parametros[0]=="(12,":
        return 11
        #return "december"
    else:
        return "Index Error"
        #return "NONE"

# Return legend with months and hours as Strings
def get_hour_from_header(cabecera):
    #parametros = list(cabecera)
    parametros = cabecera.split()
    #print(f"La lista de parametros es: {parametros}\n")
    #print(f"La hora es {parametros[7]}")
    #return parametros[7]
    if parametros[2]=="1)":
        return '0'
    elif parametros[2]=="2)":
        return '1'
    elif parametros[2]=="3)":
        return '2'
    elif parametros[2]=="4)":
        return '3'
    elif parametros[2]=="5)":
        return '4'
    elif parametros[2]=="6)":
        return '5'
    elif parametros[2]=="7)":
        return '6'
    elif parametros[2]=="8)":
        return '7'
    elif parametros[2]=="9)":
        return '8'
    elif parametros[2]=="10)":
        return '9'
    elif parametros[2]=="11)":
        return '10'
    elif parametros[2]=="12)":
        return '11'
    else:
        return "Index Error"
        #return "NONE"

def get_month_from_header(cabecera):
    #parametros = list(cabecera)   
    #return parametros[1]
    parametros = cabecera.split()
    if parametros[0]=="(1,":
        return "January"
        #return "january"
    elif parametros[0]=="(2,":
        return "February"
        #return "february"
    elif parametros[0]=="(3,":
        return  "March" 
        #return "march"
    elif parametros[0]=="(4,":
        return "April" 
        #return "april"
    elif parametros[0]=="(5,":
        return "May" 
        #return "may"
    elif parametros[0]=="(6,":
        return "June" 
        #return "june"
    elif parametros[0]=="(7,":
        return "July" 
        #return "july"
    elif parametros[0]=="(8,":
        return "August" 
        #return "august"
    elif parametros[0]=="(9,":
        return "September" 
        #return "september"
    elif parametros[0]=="(10,":
        return "October" 
        #return "october"
    elif parametros[0]=="(11,":
        return "November" 
        #return "november"
    elif parametros[0]=="(12,":
        return "December"
        #return "december"
    else:
        return "Index Error"
        #return "NONE"

def get_cdi_index_pho4d(dfDatas):
    '''
    - CDI parameter calc
    Escala de valores de iluminancia: 0lx, 50lx, 100lx, 200lx, 300lx, 500lx, 750lx, 1000lx, 2000lx

    1 - Del dataset filtrar por zona 
    2 - Tomar los valores por hora y contar las veces que ocurre la condición según la escala de iluminancia predefinida ("Threshold" en planilla excel)
    3 - El valor calculado en el punto 2 se debe *100 y dividir por la cantidad de puntos de la zona analizada para cada hora por cada valor de la 
    escala de iluminancia ("Threshold%" en planilla excel)
    4 - Si el valor calculado de Threshold% es igual o mayor a 50% (del tiempo?) (valor configurable?) se indica el valor de iluminancia de la escala 
    de iluminancia predefinida correspondiente, en caso contrario se indica como NaN ("CDI_sensor" en planilla excel)
    5 - El valor de CDI para cada hora es el mayor valor de iluminancia predefinida que supera el 50% (del tiempo?) calculado en el punto 4
    6 - Contabilizar la cantidad de horas que superan el setPointCDI (300 en el excel) y calcular el porcentaje sobre la totalidad de las horas

    
    nHours - number of columns of dataset that represents the hours
    nSensors - number of rows of dataset that represent the number of sensor in the space under study


    Input Parameters
        dfDatas -  Pandas Dataframe with data 
    
    Output Parameters
        cdiValues - dataframe, max iluminance value by sensor
        scdiValues - dictionary with sCDI values for iluminance scale: 0lx, 50lx, 100lx, 200lx, 300lx, 500lx, 750lx, 1000lx, 2000lx
    '''

    nHours = len(list(dfDatas.columns)) - 5
    nSensors = len(dfDatas.index)
    print("---------------------------------")
    print(f"HOURS: {nHours} ")
    print(f"NUMBER OF SENSORS: {nSensors} ")
    print("---------------------------------")

    cdiMenor50 = np.zeros(nHours, dtype=float)
    cdiMayor50 = np.zeros(nHours, dtype=float)
    cdiMayor100 = np.zeros(nHours, dtype=float)
    cdiMayor200 = np.zeros(nHours, dtype=float)
    cdiMayor300 = np.zeros(nHours, dtype=float)
    cdiMayor500 = np.zeros(nHours, dtype=float)
    cdiMayor750 = np.zeros(nHours, dtype=float)
    cdiMayor1000 = np.zeros(nHours, dtype=float)
    cdiMayor2000 = np.zeros(nHours, dtype=float)

    cdiMenor50Aux = np.zeros(nHours, dtype=float)
    cdiMayor50Aux = np.zeros(nHours, dtype=float)
    cdiMayor100Aux = np.zeros(nHours, dtype=float)
    cdiMayor200Aux = np.zeros(nHours, dtype=float)
    cdiMayor300Aux = np.zeros(nHours, dtype=float)
    cdiMayor500Aux = np.zeros(nHours, dtype=float)
    cdiMayor750Aux = np.zeros(nHours, dtype=float)
    cdiMayor1000Aux = np.zeros(nHours, dtype=float)
    cdiMayor2000Aux = np.zeros(nHours, dtype=float)

    cdiValues = np.zeros(nHours,dtype=float)
    
    # DETERMIANR LA CANTIDAD DE SENSORES CORRESPONDIENTE AL PORCETAJE SELECCIONADO
    cdiSensorsPercent = 100 * float(cdiSensorFraction)

    print(f"\nCDI - Porcentaje de sensores considerados: {cdiSensorsPercent:.2f} %\n")
         
    dfDatasValues = pd.DataFrame()

    dfDatasValues = dfDatas.iloc[:, 5:len(list(dfDatas.columns))].copy()
    #print(f"LOS DATOS A PROCESAR SON \n {dfDatasValues}") 

    dfCDIVector = dfDatas[[dfDatas.columns[5]]].copy() # permite generar un array con la misma cantida de filas que el dataFrame que recibimos
    dfCDIVector[:] = 0  

    #print(f"LOS DATOS A PROCESAR SON \n {dfDatasValues}") 
    #print(f"LA CANTIDAD DE COLUMNAS SON \n {dfCDIVector.shape}")

    dfDatasValues.columns = [i for i in range(dfDatasValues.shape[1])]
    #print(f"LOS NOMBRES DE LAS COLUMNAS SON: {dfDatasValues.columns}")

    for hs in range(dfDatasValues.shape[1]):        
        try:            
            dfCDIVector.loc[(dfDatasValues[hs] < 50), dfCDIVector.columns[0]] = 1
            cdiMenor50[hs] = dfCDIVector[dfCDIVector.columns[0]].sum()
            dfCDIVector[:] = 0        

            dfCDIVector.loc[(dfDatasValues[hs] >= 50), dfCDIVector.columns[0]] = 1
            cdiMayor50[hs] = dfCDIVector[dfCDIVector.columns[0]].sum()
            dfCDIVector[:] = 0

            dfCDIVector.loc[(dfDatasValues[hs] >= 100), dfCDIVector.columns[0]] = 1
            cdiMayor100[hs] = dfCDIVector[dfCDIVector.columns[0]].sum()
            dfCDIVector[:] = 0

            dfCDIVector.loc[(dfDatasValues[hs] >= 200), dfCDIVector.columns[0]] = 1
            cdiMayor200[hs] = dfCDIVector[dfCDIVector.columns[0]].sum()
            dfCDIVector[:] = 0

            dfCDIVector.loc[(dfDatasValues[hs] >= 300), dfCDIVector.columns[0]] = 1
            cdiMayor300[hs] = dfCDIVector[dfCDIVector.columns[0]].sum()
            dfCDIVector[:] = 0

            dfCDIVector.loc[(dfDatasValues[hs] >= 500), dfCDIVector.columns[0]] = 1
            cdiMayor500[hs] = dfCDIVector[dfCDIVector.columns[0]].sum()
            dfCDIVector[:] = 0

            dfCDIVector.loc[(dfDatasValues[hs] >= 750), dfCDIVector.columns[0]] = 1
            cdiMayor750[hs] = dfCDIVector[dfCDIVector.columns[0]].sum()
            dfCDIVector[:] = 0

            dfCDIVector.loc[(dfDatasValues[hs] >= 1000), dfCDIVector.columns[0]] = 1
            cdiMayor1000[hs] = dfCDIVector[dfCDIVector.columns[0]].sum()
            dfCDIVector[:] = 0

            dfCDIVector.loc[(dfDatasValues[hs] >= 2000), dfCDIVector.columns[0]] = 1
            cdiMayor2000[hs] = dfCDIVector[dfCDIVector.columns[0]].sum()     
            dfCDIVector[:] = 0         

            cdiMenor50Aux[hs] = cdiMenor50[hs] * 100 / nSensors
            cdiMayor50Aux[hs] = cdiMayor50[hs] * 100 / nSensors
            cdiMayor100Aux[hs] = cdiMayor100[hs] * 100 / nSensors
            cdiMayor200Aux[hs] = cdiMayor200[hs] * 100 / nSensors
            cdiMayor300Aux[hs] = cdiMayor300[hs] * 100 / nSensors
            cdiMayor500Aux[hs] = cdiMayor500[hs] * 100 / nSensors
            cdiMayor750Aux[hs] = cdiMayor750[hs] * 100 / nSensors
            cdiMayor1000Aux[hs] = cdiMayor1000[hs] * 100 / nSensors
            cdiMayor2000Aux[hs] = cdiMayor2000[hs] * 100 / nSensors

            if cdiMenor50Aux[hs] >= cdiSensorsPercent:
                cdiValues[hs] = 0
            if cdiMayor50Aux[hs] >= cdiSensorsPercent:
                cdiValues[hs] = 50
            if cdiMayor100Aux[hs] >= cdiSensorsPercent:
                cdiValues[hs] = 100
            if cdiMayor200Aux[hs] >= cdiSensorsPercent:
                cdiValues[hs] = 200
            if cdiMayor300Aux[hs] >= cdiSensorsPercent:
                cdiValues[hs] = 300
            if cdiMayor500Aux[hs] >= cdiSensorsPercent:
                cdiValues[hs] = 500
            if cdiMayor750Aux[hs] >= cdiSensorsPercent:
                cdiValues[hs] = 750
            if cdiMayor1000Aux[hs] >= cdiSensorsPercent:
                cdiValues[hs] = 1000
            if cdiMayor2000Aux[hs] >= cdiSensorsPercent:
                cdiValues[hs] = 2000
        except:
            print(f"Couldn't find a match for the key: {hs}")
    

    print(cdiValues)
    cdiMatrix = np.reshape(cdiValues, (12,12))
    print(cdiMatrix)

    return cdiValues


'''
def get_cdi_index(dmcNsensors, dmcRealHours, dmcCondicion, dfResultados):
    """"
    - CALCULO DE PARÁMETRO CDI
    Escala de valores de iluminancia: 0lx, 50lx, 100lx, 200lx, 300lx, 500lx, 750lx, 1000lx, 2000lx

    Parámetros Input
        dmcNsensors -  cantida de sensores 
        dmcRealHours - cantidad de horas a considerar 
        dmcCondicion - condición de ocupación, y horas a considerar
        dfResultados - dataFrame con los valores de iluminancia de todos los sensores a analizar

    Parámetros Output
        cdiValues - dataframe, valor de máxima iluminancia por sensor, segun escala
        sCDIvalues - porcentaje de sensores para cada rango de la escala indicada

    """"
    cdiMenor50 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor50 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor100 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor200 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor300 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor500 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor750 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor1000 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor2000 = np.zeros(dmcNsensors, dtype=float)

    cdiMenor50Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor50Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor100Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor200Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor300Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor500Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor750Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor1000Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor2000Aux = np.zeros(dmcNsensors, dtype=float)

    cdiValues = np.zeros(dmcNsensors,dtype=float)
    cdiValue = 0.0
    sCDIvalues = { "0lx": 0, "50lx": 0, "100lx": 0, "200lx": 0, "300lx": 0, "500lx": 0, "750lx": 0, "1000lx": 0, "2000lx": 0 }
    cdi = ""

    # DETERMIANR LA CANTIDAD DE SENSORES CORRESPONDIENTE AL PORCETAJE SELECCIONADO
    cdiSensorsPercent = 100 * cdiPorcentajeSensores
    scdiSensorPercent = 100 * scdiPorcentajeSensores
    print(f"\nCDI - Porcentaje de sensores considerados: {cdiSensorsPercent:.2f} %\n")
    
    dfCDIVector = dfResultados[[dfResultados.columns[0]]].copy() # permite generar un array con la misma cantida de filas que el dataFrame que recibimos
    dfCDIVector[:] = 0    
    
    for sensor in range(dfResultados.shape[1]):
        dfCDIVector.loc[((dfResultados[sensor] < 50) & (dmcCondicion['condicion'] == 1)), dfCDIVector.columns[0]] = 1
        cdiMenor50[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0        

        dfCDIVector.loc[(dfResultados[sensor] >= 50) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor50[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 100) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor100[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 200) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor200[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 300) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor300[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 500) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor500[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 750) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor750[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 1000) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor1000[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 2000) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor2000[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()     
        dfCDIVector[:] = 0         

        cdiMenor50Aux[sensor] = cdiMenor50[sensor] * 100 / dmcRealHours
        cdiMayor50Aux[sensor] = cdiMayor50[sensor] * 100 / dmcRealHours
        cdiMayor100Aux[sensor] = cdiMayor100[sensor] * 100 / dmcRealHours
        cdiMayor200Aux[sensor] = cdiMayor200[sensor] * 100 / dmcRealHours
        cdiMayor300Aux[sensor] = cdiMayor300[sensor] * 100 / dmcRealHours
        cdiMayor500Aux[sensor] = cdiMayor500[sensor] * 100 / dmcRealHours
        cdiMayor750Aux[sensor] = cdiMayor750[sensor] * 100 / dmcRealHours
        cdiMayor1000Aux[sensor] = cdiMayor1000[sensor] * 100 / dmcRealHours
        cdiMayor2000Aux[sensor] = cdiMayor2000[sensor] * 100 / dmcRealHours

        if cdiMenor50Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 0
        if cdiMayor50Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 50
        if cdiMayor100Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 100
        if cdiMayor200Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 200
        if cdiMayor300Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 300
        if cdiMayor500Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 500
        if cdiMayor750Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 750
        if cdiMayor1000Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 1000
        if cdiMayor2000Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 2000
        
        if int(cdiValues[sensor]) == 0:
            sCDIvalues["0lx"] = sCDIvalues["0lx"] + 1
        if int(cdiValues[sensor]) == 50:
            sCDIvalues["50lx"] = sCDIvalues["50lx"] + 1
        if int(cdiValues[sensor]) == 100:
            sCDIvalues["100lx"] = sCDIvalues["100lx"] + 1
        if int(cdiValues[sensor]) == 200:
            sCDIvalues["200lx"] = sCDIvalues["200lx"] + 1
        if int(cdiValues[sensor]) == 300:
            sCDIvalues["300lx"] = sCDIvalues["300lx"] + 1
        if int(cdiValues[sensor]) == 500:
            sCDIvalues["500lx"] = sCDIvalues["500lx"] + 1
        if int(cdiValues[sensor]) == 750:
            sCDIvalues["750lx"] = sCDIvalues["750lx"] + 1
        if int(cdiValues[sensor] )== 1000:
            sCDIvalues["1000lx"] = sCDIvalues["1000lx"] + 1
        if int(cdiValues[sensor]) == 2000:
            sCDIvalues["2000lx"] = sCDIvalues["2000lx"] + 1
    
    
    print(f"valores de sCDI: {sCDIvalues}")
    for k in sCDIvalues:
        sCDIvalues[k] = sCDIvalues[k]*100/dmcNsensors 
    
    for k in sCDIvalues:
        cdiValue += sCDIvalues[k]
        cdi = k
        if (cdiValue >= cdiPorcentajeSensores*100):
            break

    print(f"Valores de sCDI normalizados: < 50lx: {sCDIvalues['0lx']:.2f} >= 50lx: {sCDIvalues['50lx']:.2f}, >= 100lx: {sCDIvalues['100lx']:.2f}, >= 200lx: {sCDIvalues['200lx']:.2f}, >= 300lx: {sCDIvalues['300lx']:.2f}, >= 500lx: {sCDIvalues['500lx']:.2f}, >= 750lx: {sCDIvalues['750lx']:.2f}, >= 1000lx: {sCDIvalues['1000lx']:.2f}, >= 2000lx: {sCDIvalues['2000lx']:.2f}\n")
    
    return cdiValues, sCDIvalues, cdi

'''


def read_config_file(config_file_path):
    '''
    Read the configuration file and set de variables 
    kword:
        CDI
        DP = Data Path
        RP = Results Path
        HS = Hour Start
        HE = Hour End
        MS = Month Start
        ME = Month End

    '''
    config = configparser.ConfigParser()
    config = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    config.read(config_file_path)

    #print(config.sections())

    filesPathData = config['PATHS']['data_file_path']
    filesPathSaveCSV = config['PATHS']['csv_save_path']
    
    hour_start = config['FILTER']['hour_start']
    hour_end = config['FILTER']['hour_end']
    #month_start = config['FILTER']['month_start']
    #month_end = config['FILTER']['month_end']

    cdiSensorFraction = config['PARAMETERS']['cdiSensorFraction']
    cdiSetpoint = config['PARAMETERS']['cdiSetpoint']

    configValues = {'hsStart': config['FILTER']['hour_start'],
                    'hsEnd': config['FILTER']['hour_end'],
                    'filePath': config['PATHS']['data_file_path'],
                    'cdiSensorFraction': config['PARAMETERS']['cdiSensorFraction']}

    
    #print(filesPathData)
    #print(configValues)

    return filesPathData, hour_start, hour_end, cdiSensorFraction, cdiSetpoint, filesPathSaveCSV


def create_file(filesPath, dfData):
    '''
    - GENERACIÓN DE ARCHIVOS CON LOS DATOS UNIFICADOS
        Se genera el archivo "unificado" con los datos calculados, en el directorio indicado.
    
    Parámetros Input
        filesPath - Elemento tipo String, indica la ruta a la carpeto donde se guardará el archivo
        dfData - Elemento tipo Panda dataframe, contiene la información a guardar en el archivo
        
    Parámetros Output
        archivo unificado generado en el filePath indicado

    '''
    print(dfData)

    if os.path.isdir(filesPath):
        #print("La carpeta existe")
        path = filesPath
    else:
        os.mkdir(filesPath)
        path = filesPath
        #print(f"Se creo la carpeta results la ruta es {path}")

    '''creationSuccess = dfData.to_csv(path+'results_ph4dt.csv', index = False ,mode='a')

    if creationSuccess != None:
        print("Creation of file OK")
        return 1
    else:
        print("Problem with creation of file")
        return 0'''
    
    try:
        dfData.to_csv(path+'results_pho4dt.csv', index = False ,mode='a')
        print(f"Creation of file OK on {path}")

    except:
        print("Problem with creation of file")


def get_sCDi (index, dfData):

    normalizeValues = {}

    values = {
        "0lx": 0,
        "50lx": 0,
        "100lx": 0,
        "200lx": 0,
        "300lx": 0,
        "500lx": 0,
        "750lx": 0,
        "1000lx": 0,
        "2000lx": 0
    }

    countsValues = dfData.value_counts("cdi", normalize=True, ascending=True)
    normalizeValues = countsValues.to_dict()

    #print(normalizeValues)

    if 0.0 in normalizeValues:
        values["0lx"] = round(normalizeValues[0.0]*100, 2)
    else:
        values["0lx"] = 0.0

    if 50.0 in normalizeValues:
        values["50lx"] = round(normalizeValues[50.0]*100, 2)
    else:
        values["50lx"] = 0.0
    
    if 100.0 in normalizeValues:
        values["100lx"] = round(normalizeValues[100.0]*100, 2)
    else:
        values["100lx"] = 0.0
    
    if 200.0 in normalizeValues:
        values["200lx"] = round(normalizeValues[200.0]*100, 2)
    else:
        values["200lx"] = 0.0
    
    if 300.0 in normalizeValues:
        values["300lx"] = round(normalizeValues[300.0]*100, 2)
    else:
        values["300lx"] = 0.0
    
    if 500.0 in normalizeValues:
        values["500lx"] = round(normalizeValues[500.0]*100, 2)
    else:
        values["500lx"] = 0.0
    
    if 750.0 in normalizeValues:
        values["750lx"] = round(normalizeValues[750.0]*100, 2)
    else:
        values["750lx"] = 0.0

    if 1000.0 in normalizeValues:
        values["1000lx"] = round(normalizeValues[1000.0]*100, 2)
    else:
        values["1000lx"] = 0.0

    if 2000.0 in normalizeValues:
        values["2000lx"] = round(normalizeValues[2000.0]*100, 2)
    else:
        values["2000lx"] = 0.0


    #print(values)

    return values


''' - INICIO PROGRAMA PRINCIPAL - '''

# Read config file
try:
    filesPathData, hour_start, hour_end, cdiSensorFraction, cdiSetpoint, filesPathSaveCSV = read_config_file(cnf_path)    
    print("Config file OK")

except:
    print("Error on configuration file")
    exit(0)

print(f"Data file: {filesPathData}")

dfDatas = pd.read_csv(filesPathData, sep='\t', header=2)

cabeceras = list(dfDatas.columns)
print(f"Headers of dataframe:\n{cabeceras}")

hoursQuantity = len(cabeceras)-5

print(f"Hours to proccess: {hoursQuantity}")

zones = dfDatas[cabeceras[0]].value_counts(sort=False).index
zonesNumberOfSensors = dfDatas[cabeceras[0]].value_counts(sort=False).to_dict() # dict with zones as key and number of sensor as values

print(f"The zones are:\n{zones}")

tablaDatos = dict()
print(dfDatas["# zone"].unique().tolist())

cdiMatrix = pd.DataFrame()
#cdiMatrix = pd.DataFrame(columns=["# zone", "cdi"])
df_cdi = pd.DataFrame(columns = ['zones', 'cdi'], index=[0])

#df_mct_ = pd.DataFrame(columns=['zones', 'month', 'mct'], index=[0])
#df_aux = pd.DataFrame(columns=['opacity'], index=[0])
df_mct = {}
df_aux2 = []
cdi_data = {}
df_global = {}

for zone in zones:
    df_mct[zone] = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct'], index=[0])
    cdi_data[zone] = pd.DataFrame(columns=['cdi'], index=[0])
    df_global[zone] = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct', 'cdi'], index=[0])


# The function get_cdi_pho4d() should return a pandas dataframe with zone and cdi columns
for zone in dfDatas["# zone"].unique().tolist():
    cdies = get_cdi_index_pho4d(dfDatas.loc[(dfDatas["# zone"] == zone)])    
    print(f"Los datos de CDI son: \n{cdies}")
    #data[zone] = {'cdi': cdies}
    #data = {'zones': [str(zone) for i in range(0, len(cdies))], 'cdi': cdies}
    #data_df = pd.DataFrame(data)
    #df_cdi = pd.concat([df_cdi, data_df], ignore_index=True)
    for element in cdies:
        cdi_data[zone] = pd.concat([cdi_data[zone], pd.DataFrame({'cdi': [element]})], ignore_index=True, axis=0)
        
print(f"Los datos de CDI son: \n{cdi_data}")

for indice in zones:
    tablaDatos[indice] = np.zeros((12,12))

    print(indice)
    #tablaDatos[indice] = pd.DataFrame(columnas)
   
#print(tablaDatos)
print(f'El tamanio de la tabla de datos es >> {getsizeof(tablaDatos)}')

#df_mct = pd.DataFrame({'zones':[], 'month':[], 'hour':[], 'mct':[]})
#df_mct = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct'], index=[0])
#df_mct = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct'], index=[0])



print(f"LOS DATOS DE df_mct SON \n {df_mct}")

#Create dataFrame with mct values for each 'Zone'
for element in range (5,len(cabeceras)):
    mct_values = dfDatas.groupby("# zone")[cabeceras[element]].median()
    #print(f"LOS VALORES MEDIOS SON \n {mct_values}")
    hour = get_hour_from_header(cabeceras[element])
    month = get_month_from_header(cabeceras[element])

    hour_int = get_hour_from_header_int(cabeceras[element])
    month_int = get_month_from_header_int(cabeceras[element])
    
    for indice in mct_values.index:        
        df_mct[indice] = pd.concat([df_mct[indice], pd.DataFrame({'zones': [indice], 'month':[month], 'hour': [hour], 'mct': [mct_values[indice]]})], ignore_index=True, axis=0)
        
        #df_aux2[indice] = pd.DataFrame({'zones': [indice], 'month':[month], 'hour': [hour], 'mct': [mct_values[indice]]})
        #df_aux2[indice] = pd.concat([df_aux2[indice], pd.DataFrame({'zones': [indice], 'month':[month], 'hour': [hour], 'mct': [mct_values[indice]]})], ignore_index=True, axis=0)
        #df_mct = pd.concat([df_mct, df[indice]], ignore_index=True, axis=0)
        #tablaDatos[indice][int(mes)][int(hora)] = mct_values[indice]


### JOIN THE VALUES OF CDI TO df_mct DATAFRAME
#print(f"LOS DATOS DE df_mct \n {df_mct}")
#df_to_plot = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct', 'cdi'], index=[0])
for indice in zones:
    df_global[indice] = pd.concat([df_mct[indice], cdi_data[indice]], axis=1)

df_to_plot = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct', 'cdi'])

for indice in zones:
    df_to_plot = pd.concat([df_to_plot, df_global[indice]], ignore_index=True, axis=0)

#xLabs = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
xLabs = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
yLabs = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


#print(f'LOS DATOS DE LA ZONA {zones[0]} es >> \n{tablaDatos[zones[0]]}')
#tabla_test = tablaDatos[zones[0]]

print(":::::::::    LOS DATOS A GUARDAR SON :::::::::")
print(df_to_plot)

indexID = []

month_start_stop = []
hour_start_stop = []
cdiFract = []            
CDIes = []
cdi12hs = []
cdiCustom = []

sCDI_0lx = []
sCDI_50lx = []
sCDI_100lx = []
sCDI_200lx = []
sCDI_300lx = []
sCDI_500lx = []
sCDI_750lx = []
sCDI_1000lx = []
sCDI_2000lx = []


print(zones)

for indice in zones:

    print(df_global[indice])
    sCDI_values = get_sCDi(indice, df_global[indice])
    
    indexID.append(indice)

    month_start_stop.append("January - December")
    hour_start_stop.append(str(hour_start + "-" + hour_end))
    cdiFract.append(cdiSensorFraction)            
    CDIes.append(cdiSetpoint)

    sCDI_0lx.append(sCDI_values['0lx'])
    sCDI_50lx.append(sCDI_values['50lx'])
    sCDI_100lx.append(sCDI_values['100lx'])
    sCDI_200lx.append(sCDI_values['200lx'])
    sCDI_300lx.append(sCDI_values['300lx'])
    sCDI_500lx.append(sCDI_values['500lx'])
    sCDI_750lx.append(sCDI_values['750lx'])
    sCDI_1000lx.append(sCDI_values['1000lx'])
    sCDI_2000lx.append(sCDI_values['2000lx'])

print("LOS VALRES DE DE sCDI SON:")
print (indexID)
print (month_start_stop)
print(hour_start_stop)
print (sCDI_values)


resultados = {
                "ID" : indexID, 
                "month_start-month_end" : month_start_stop,
                "hour_start-hour_end": hour_start_stop, 
                "cdiSensorFraction": cdiFract,            
                "CDI": CDIes,
                "sCDI-0lx": sCDI_0lx,
                "sCDI-50lx": sCDI_50lx,
                "sCDI-100lx": sCDI_100lx,
                "sCDI-200lx": sCDI_200lx,
                "sCDI-300lx": sCDI_300lx,
                "sCDI-500lx": sCDI_500lx,
                "sCDI-750lx": sCDI_750lx,
                "sCDI-1000lx": sCDI_1000lx,
                "sCDI-2000lx": sCDI_2000lx                
            }

print(resultados)

dfUnificados = pd.DataFrame(resultados)
print (dfUnificados)
       
create_file(filesPathSaveCSV, dfUnificados)

###########################
### GRAPHICS SECTIONS   ###
###########################


fig = go.Figure()

fig = go.Figure(go.Heatmap(
        x=[i for i in range(1, 13)], 
        y=[i for i in range(1, 13)], 
        z=df_to_plot[df_to_plot["zones"]==zones[0]]["mct"].values.reshape((12,12)),
        zmin=0,
        zmax=2000,
        text=df_to_plot[df_to_plot["zones"]==zones[0]]["mct"].values.reshape((12,12)),
        texttemplate="%{text:.2f}",
        name=zones[0],
        colorscale='jet',
        hovertemplate =
                '<b>Month</b>: %{y}<br>'+
                '<b>Hour</b>: %{x}<br>'+
                '<b>Ilum[lux]</b>:<b>%{z:.2f}</b>',
        xgap=1, 
        ygap=1,
        colorbar=dict(
            tickvals = [0, 50, 100, 200, 300, 500, 750, 1000, 2000]
        )
        
    ))


'''
#for zones in list(df_mct["zones"].unique()):

### Create data selector for diferent Metrics ###
metrics = ["mct", "cdi"]
buttons_metrics = []
metric = "mct"
# create metric dropdown menu

for m in range(0,len(metrics)):
    buttons_metrics.append(
        dict(
            args=[{metric: metrics[m],
                   "text":metrics[m],
                   "name":metrics[m]
                   }],
            label = metrics[m],
            method = "update")
     )

'''
### Create data selector for diferent Zones ###
# create zones dropdown menu
buttons_zones = []
for z in range(0,len(zones)):
    buttons_zones.append(
        dict(
            args=[{"z":[(df_to_plot[df_to_plot["zones"]==zones[z]]["mct"].values.reshape((12,12)))],
                   "text":[(df_to_plot[df_to_plot["zones"]==zones[z]]["mct"].values.reshape((12,12)))],
                   "name":[zones[z]]
                   }],
            label = zones[z]+" mct metric",
            method = "restyle")
     )
    buttons_zones.append(
        dict(
            args=[{"z":[(df_to_plot[df_to_plot["zones"]==zones[z]]["cdi"].values.reshape((12,12)))],
                   "text":[(df_to_plot[df_to_plot["zones"]==zones[z]]["cdi"].values.reshape((12,12)))],
                   "name":[zones[z]]
                   }],
            label = zones[z]+" CDI metric",
            method = "restyle")
     )
    

    

predifined_hour_start = int(hour_start) + 0.5
predifined_hour_stop = int(hour_end) + 1.5

#coord = [[x_lower, x_upper], [x_lower, x_upper]] primer elemento configura el rectangulo de la izquierda el segundo elemento configura el rectangulo de la derecha
#coord = [[1, 4], [7, 13]]

coord = [[1, 1], [13, 13]]
ply_shapes = {}
opacity_value = 0.8
for i in range(0,2):
    ply_shapes['shape_'+str(i)] = go.layout.Shape(type="rect",
                                                  x0=coord[i][0] - 0.5,
                                                  x1=coord[i][1] - 0.5,
                                                  y0=0.5,
                                                  y1=12.5,
                                                  line=dict(
                                                    color="gray",
                                                    width=2,
                                                    ),
                                                  fillcolor="gray",
                                                  opacity=opacity_value)


buttons_shapes = [
    dict(args=[{'shapes[0].visible': False,
                'shapes[1].visible': False,                
                }], 
         label= 'No Filter', 
         method='relayout'
         ),
    
    dict(args=[{'shapes[0].visible': True,
                'shapes[1].visible': True,
                'shapes[0].x0': predifined_hour_stop, 
                'shapes[0].x1': 12.5,
                'shapes[1].x0': 0.5,
                'shapes[1].x1': predifined_hour_start
                }], 
         label= 'Predifined', 
         method='relayout'
         ),

    dict(args=[{'shapes[0].visible': True,
                'shapes[1].visible': False,
                'shapes[0].x0': 6.5, 
                'shapes[0].x1': 12.5
                }], 
         label= 'Morning', 
         method='relayout'
         ),

    dict(args=[{'shapes[0].visible': False,
                'shapes[1].visible': True,
                'shapes[1].x0': 0.5,
                'shapes[1].x1': 6.5,
                }], 
         label= 'Afternoon', 
         method='relayout'
         )    
]

lst_shapes=list(ply_shapes.values())
fig.update_layout(shapes=lst_shapes)

button_layer_metrics_height = -0.15
button_layer_zones_height = -0.1
button_layer_filter_height = -0.2

fig.update_layout(
    autosize=False,
    width=1500,
    height=650,
    margin = dict (t = 0, b = 0.5, l = 0, r = 0))


fig.update_layout(
    updatemenus=[go.layout.Updatemenu(buttons=buttons_zones,
                                        type = "dropdown",
                                        direction="up",
                                        pad={"b": 10, "r": 10},
                                        showactive=True,
                                        x=0.04,
                                        xanchor="left",
                                        y=button_layer_zones_height,
                                        yanchor="bottom",
                                        bgcolor="#dadada"),
                go.layout.Updatemenu(buttons=buttons_shapes,
                                        type = "buttons",
                                        direction="right",
                                        pad={"b": 20, "r": 10},
                                        showactive=True,
                                        x=0.04,
                                        xanchor="left",
                                        y=button_layer_filter_height,
                                        yanchor="bottom",
                                        bgcolor="#dadada")]
)

fig.update_layout(
    annotations=[
        dict(text="Zones", 
            x=0, xref="paper", 
            y=button_layer_zones_height+0.04, 
            yref="paper",
            align="left", 
            showarrow=False),
        dict(text="Filter", 
            x=0, xref="paper", 
            y=button_layer_filter_height+0.05,
            yref="paper", 
            showarrow=False)
    ])

'''fig.update_layout(
    updatemenus=[go.layout.Updatemenu(buttons=buttons_metrics,
                                        type = "dropdown",
                                        direction="right",
                                        pad={"b": 10, "r": 10},
                                        showactive=True,
                                        x=0.04,
                                        xanchor="left",
                                        y=button_layer_metrics_height,
                                        yanchor="bottom"),
                go.layout.Updatemenu(buttons=buttons_zones,
                                        type = "dropdown",
                                        direction="right",
                                        pad={"b": 10, "r": 10},
                                        showactive=True,
                                        x=0.04,
                                        xanchor="left",
                                        y=button_layer_zones_height,
                                        yanchor="bottom"),
                go.layout.Updatemenu(buttons=buttons_shapes,
                                        type = "buttons",
                                        direction="right",
                                        pad={"b": 20, "r": 10},
                                        showactive=True,
                                        x=0.04,
                                        xanchor="left",
                                        y=button_layer_filter_height,
                                        yanchor="bottom")]
)

fig.update_layout(
    annotations=[
        dict(text="Metrics", 
            x=0, xref="paper", 
            y=button_layer_metrics_height+0.04, 
            yref="paper",
            align="left", 
            showarrow=False),
        dict(text="Zones", 
            x=0, xref="paper", 
            y=button_layer_zones_height+0.04, 
            yref="paper",
            align="left", 
            showarrow=False),
        dict(text="Filter", 
            x=0, xref="paper", 
            y=button_layer_filter_height+0.05,
            yref="paper", 
            showarrow=False)
    ])'''


fig.update_yaxes(
    autorange="reversed",
    tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,12],
    ticktext=['Jan. ', 'Feb. ', 'March ', 'April ', 'May ', 'June ',
            'July ', 'Aug. ', 'Sep. ', 'Oct. ', 'Nov. ', 'Dec. '],
    showgrid=False, 
    zeroline=False, 
    fixedrange=True, 
    showline=False,
    showdividers=False, 
    showticklabels=True,
    title='MONTHS',
    )

fig.update_xaxes(
    side='top',
    nticks=12,
    tickvals= [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,12], #[i for i in range(0, 12)],
    ticktext= xLabs, #[i for i in range(0, 12)],
    showgrid=False, 
    zeroline=False, 
    fixedrange=True, 
    showline=False,
    ticks="outside", 
    ticklen=5, 
    tickcolor='#fff',
    showdividers=False, 
    showticklabels=True,
    title='HOURS',
    type="linear"                
    )



fig.show()

