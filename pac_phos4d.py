#-*- coding: utf-8 -*-
'''
TEST DE LIBRERIAS kUFFLINGS Y PLOTLY

Autores: 
    PhD. Juan Manuel Monteoliva
    Ing. Emanuel R. Schumacher
    
    
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
import json

# RUTA DE ARCHIVOS A PROCESAR

filesPath = './'
cnf_path = './setup.cfg'

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
    #print(f"ZONE: {dfDatas["# zone"]}")
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
    cdiSensorsPercent = 100 * float(parameters["CDI_SENSOR_FRACTION"])

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

    configValues = {
        "DATA_FILE_PATH": "",
        "CSV_SAVE_PATH": "",
        "HOUR_START": "0",
        "HOUR_END": "11",
        "MONTH_START": "0",
        "MONTH_END": "11",
        "CDI_SENSOR_FRACTION": "0.5"
    }

    '''filesPathData = config['PATHS']['data_file_path']
    filesPathSaveCSV = config['PATHS']['csv_save_path']
    
    hour_start = config['FILTER']['hour_start']
    hour_end = config['FILTER']['hour_end']
    #month_start = config['FILTER']['month_start']
    #month_end = config['FILTER']['month_end']

    cdiSensorFraction = config['PARAMETERS']['cdiSensorFraction']
    #cdiSetpoint = config['PARAMETERS']['cdiSetpoint']'''

    configValues = {
        "DATA_FILE_PATH": config['PATHS']['data_file_path'],
        "CSV_SAVE_PATH": config['PATHS']['csv_save_path'],
        "HOUR_START": config['FILTER']['hour_start'],
        "HOUR_END": config['FILTER']['hour_end'],
        "MONTH_START": config['FILTER']['month_start'],
        "MONTH_END": config['FILTER']['month_end'],
        "CDI_SENSOR_FRACTION": config['PARAMETERS']['cdiSensorFraction']
    }      

    print(f"Los valores de configuracion son \n {configValues}")
    return configValues

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
        dfData.to_csv(path+'results_pac.csv', index = False ,mode='a')
        print(f"Creation of file OK on {path}")

    except:
        print("Problem with creation of file")

def get_sCDI (dfData):

    normalizeValues = {}

    values = {
        "2000lx": 0,        
        "1000lx": 0,
        "750lx": 0,
        "500lx": 0,
        "300lx": 0,
        "200lx": 0,
        "100lx": 0,
        "50lx": 0,
        "0lx": 0
    }

    countsValues = dfData.value_counts("cdi", normalize=True, ascending=True)
    normalizeValues = countsValues.to_dict()

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

    return values

def get_cdi_from_sCDI(sCDI):    
    ''' 
    Get CDI value from sCDI values

    Input 
    sCDI values in dictionary format key:value >> 50lx:20.56

    Output
    cdi value, Int format 

    '''

    cdi = "0lx"
    p = 0.0
    print(sCDI)

    for k in sCDI:
        p = sCDI[k] + p
        if p >= 50.00:
            cdi = k
            break
        else:
            continue
    
    if cdi == '0lx':
        cdiValue = 0
    elif cdi == '50lx':
        cdiValue = 50
    elif cdi == '100lx':
        cdiValue = 100
    elif cdi == '200lx':
        cdiValue = 200
    elif cdi == '300lx':
        cdiValue = 300
    elif cdi == '500lx':
        cdiValue = 500
    elif cdi == '750lx':
        cdiValue = 750
    elif cdi == '1000lx':
        cdiValue = 1000
    elif cdi == '2000lx':
        cdiValue = 2000    
    
    print(f"El valor de CDI es {cdiValue}")

    return cdiValue


''' - START - '''

# Read config file
parameters = {}
try:
    #filesPathData, hour_start, hour_end, cdiSensorFraction, filesPathSaveCSV = read_config_file(cnf_path)    
    parameters = read_config_file(cnf_path)
    print(f"Config parameters >>\n {parameters} \n")
    print("Config file OK")

except:
    print("Error on configuration file")
    exit(0)

try:
    dfDatas = pd.read_csv(parameters["DATA_FILE_PATH"], sep='\t', header=2)
    #dfDatas = pd.read_csv(parameters['FILES_PATH_DATA'], sep='\t', header=2)
    print("Data file OK")

except:
    print("Error on Data file")
    exit(0)


hour_start = int(parameters["HOUR_START"])
hour_end = int(parameters["HOUR_END"])
month_start = int(parameters["MONTH_START"])
month_end = int(parameters["MONTH_END"])



    #verify the hours range is correct and ( hour_start < hour_end))
if ((1 <= hour_start <= 12) and (1 <= hour_end <= 12)):
        print("Values of Start and End Hour are valid")
else:
    print("The values of Start or End Hour are incorrect, please verify \n Hours must have a value between 1 and 12 \n Star Hour must be lower than End Hour")
    exit(0)


    #verify the month range is correct
if (1 <= month_start <= 12 and 1 <= month_end <= 12 ):
        print("Values of Start and End Month are valid")
else:
    print("The values of Start or End Month are incorrect, please verify \n Months must have a value between 1 and 12")
    exit(0)


headers = list(dfDatas.columns)
#print(f"Headers of dataframe:\n{headers}")

hoursQuantity = len(headers)-5

print(f"Hours to proccess: {hoursQuantity}")

zones = dfDatas[headers[0]].value_counts(sort=False).index
zonesNumberOfSensors = dfDatas[headers[0]].value_counts(sort=False).to_dict() # dict with zones as key and number of sensor as values

print(f"The zones are:\n{zones}")

tablaDatos = dict()

print(dfDatas["# zone"].unique().tolist())

cdiMatrix = pd.DataFrame()
#cdiMatrix = pd.DataFrame(columns=["# zone", "cdi"])
df_cdi = pd.DataFrame(columns = ['zones', 'cdi'], index=[0]) ### NOT USED - review his use

#df_mct_ = pd.DataFrame(columns=['zones', 'month', 'mct'], index=[0])
#df_aux = pd.DataFrame(columns=['opacity'], index=[0])
df_mct = {}
df_aux2 = []
cdi_data = {}
df_global = {}

for zone in zones:
    df_mct[zone] = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct'])#, index=[0])
    cdi_data[zone] = pd.DataFrame(columns=['cdi'])#, index=[0])
    df_global[zone] = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct', 'cdi'])#, index=[0])


# The function get_cdi_pho4d() should return a pandas dataframe with zone and cdi columns
for zone in dfDatas["# zone"].unique().tolist():
    cdies = get_cdi_index_pho4d(dfDatas.loc[(dfDatas["# zone"] == zone)])    
    print(f"Los datos de CDI son: \n{cdies}")
    for element in cdies:
        cdi_data[zone] = pd.concat([cdi_data[zone], pd.DataFrame({'cdi': [element]})], ignore_index=True, axis=0)
        
print(f"Los datos de CDI son: \n{cdi_data}")

for indice in zones:
    tablaDatos[indice] = np.zeros((12,12))

    print(indice)
    #tablaDatos[indice] = pd.DataFrame(columnas)
   
#print(tablaDatos)
print(f'The size of DataTable is >> {getsizeof(tablaDatos)}')

#df_mct = pd.DataFrame({'zones':[], 'month':[], 'hour':[], 'mct':[]})
#df_mct = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct'], index=[0])
#df_mct = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct'], index=[0])
#print(f"LOS DATOS DE df_mct SON \n {df_mct}")

#Create dataFrame with mct values for each 'Zone'
for element in range (5,len(headers)):
    mct_values = dfDatas.groupby("# zone")[headers[element]].median()
    #print(f"LOS VALORES MEDIOS SON \n {mct_values}")
    hour = get_hour_from_header(headers[element])
    month = get_month_from_header(headers[element])

    hour_int = get_hour_from_header_int(headers[element])
    month_int = get_month_from_header_int(headers[element])
    
    for indice in mct_values.index:        
        df_mct[indice] = pd.concat([df_mct[indice], pd.DataFrame({'zones': [indice], 'month':[month_int], 'hour': [hour_int], 'mct': [mct_values[indice]]})], ignore_index=True, axis=0)
        
        #df_aux2[indice] = pd.DataFrame({'zones': [indice], 'month':[month], 'hour': [hour], 'mct': [mct_values[indice]]})
        #df_aux2[indice] = pd.concat([df_aux2[indice], pd.DataFrame({'zones': [indice], 'month':[month], 'hour': [hour], 'mct': [mct_values[indice]]})], ignore_index=True, axis=0)
        #df_mct = pd.concat([df_mct, df[indice]], ignore_index=True, axis=0)
        #tablaDatos[indice][int(mes)][int(hora)] = mct_values[indice]


### JOIN THE VALUES OF CDI TO df_mct DATAFRAME
#df_to_plot = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct', 'cdi'], index=[0])
for zone in zones:
    df_global[zone] = pd.concat([df_mct[zone], cdi_data[zone]], axis=1)

df_to_plot = pd.DataFrame(columns=['zones', 'month', 'hour', 'mct', 'cdi'])

for zone in zones:
    df_to_plot = pd.concat([df_to_plot, df_global[zone]], ignore_index=True, axis=0)

xLabs = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
yLabs = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

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

custom_sCDI_0lx = []
custom_sCDI_50lx = []
custom_sCDI_100lx = []
custom_sCDI_200lx = []
custom_sCDI_300lx = []
custom_sCDI_500lx = []
custom_sCDI_750lx = []
custom_sCDI_1000lx = []
custom_sCDI_2000lx = []

ilum_anual_mean = []
ilum_custom_mean = []

sCDI_to_plot = pd.DataFrame(columns=['zones', 'sCDI', 'sCDI_custom'])
sCDI_custom_to_plot = pd.DataFrame()

print(zones)

for indice in zones:

    print(df_global[indice])
    sCDI_values = get_sCDI(df_global[indice])   
    
    #print(df_sCDI_aux)

    print(f"::::::::::::::::::::::::::::::::::::::::::::::::")
    print(f"::::::::    FILTRADO POR HORA DE DATOS  ::::::::")
    print(f"::::::::::::::::::::::::::::::::::::::::::::::::")
    df_hs_aux = df_global[indice]

    if (hour_start > hour_end):        
        df_hs_lower = df_hs_aux[(df_hs_aux["hour"].values <= (hour_end-1))]
        df_hs_upper = df_hs_aux[(df_hs_aux["hour"].values >= (hour_start-1))]
        framesHS = [df_hs_lower, df_hs_upper]            
        df_hours = pd.concat(framesHS)

    elif(hour_start < hour_end):
        df_hours = df_hs_aux[(df_hs_aux["hour"].values >= (hour_start-1)) & (df_hs_aux["hour"].values <= (hour_end-1))]

    else:
        df_hours = df_hs_aux[(df_hs_aux["hour"].values == (hour_start-1))]
    
    print(df_hours)

    print(f"::::::::::::::::::::::::::::::::::::::::::::::::")
    print(f"::::::::::::::::::::::::::::::::::::::::::::::::")


    if (month_start < month_end):
        df_sCDI_aux = df_hours[((df_hours["month"].values >= (month_start-1))&(df_hours["month"].values <= (month_end-1)))]
        
    elif (month_start > month_end):        
        df_month_lower = df_hours[((df_hours["month"].values <= (month_end-1)))]        
        df_month_upper = df_hours[((df_hours["month"].values >= (month_start-1)))]        
        frames = [df_month_lower, df_month_upper]        
        df_sCDI_aux = pd.concat(frames)

    else:
        df_sCDI_aux = df_hours[df_hours["month"].values == (month_start-1)]
            
        
    print(df_sCDI_aux)

    sCDI_custom = get_sCDI(df_sCDI_aux)

    print(f"Los valores de sCDI son >> \n {sCDI_values}")
    print(f"Los valores de sCDI - custom son >> \n {sCDI_custom}")

    cdi12hsIndex = get_cdi_from_sCDI(sCDI_values)
    cdiCustomIndex = get_cdi_from_sCDI(sCDI_custom)
    
    indexID.append(indice)

    month_start_stop.append(str(month_start) + " - " + str(month_end))
    hour_start_stop.append(str(hour_start) + " - " + str(hour_end))
    cdiFract.append(parameters["CDI_SENSOR_FRACTION"])            
    CDIes.append(cdiSetpoint)

    
    cdiCustom.append(cdiCustomIndex)
    custom_sCDI_0lx.append(sCDI_custom['0lx'])
    custom_sCDI_50lx.append(sCDI_custom['50lx'])
    custom_sCDI_100lx.append(sCDI_custom['100lx'])
    custom_sCDI_200lx.append(sCDI_custom['200lx'])
    custom_sCDI_300lx.append(sCDI_custom['300lx'])
    custom_sCDI_500lx.append(sCDI_custom['500lx'])
    custom_sCDI_750lx.append(sCDI_custom['750lx'])
    custom_sCDI_1000lx.append(sCDI_custom['1000lx'])
    custom_sCDI_2000lx.append(sCDI_custom['2000lx'])

    cdi12hs.append(cdi12hsIndex)    
    sCDI_0lx.append(sCDI_values['0lx'])
    sCDI_50lx.append(sCDI_values['50lx'])
    sCDI_100lx.append(sCDI_values['100lx'])
    sCDI_200lx.append(sCDI_values['200lx'])
    sCDI_300lx.append(sCDI_values['300lx'])
    sCDI_500lx.append(sCDI_values['500lx'])
    sCDI_750lx.append(sCDI_values['750lx'])
    sCDI_1000lx.append(sCDI_values['1000lx'])
    sCDI_2000lx.append(sCDI_values['2000lx'])


    ilum_anual_mean.append(df_hs_aux["mct"].mean())
    ilum_custom_mean.append(df_sCDI_aux["mct"].mean())

    print(ilum_anual_mean)
    print(ilum_custom_mean)

    dicc = {key: value for key, value in sCDI_values.items() if value > 0.00}
    dicc_custom = {key: value for key, value in sCDI_custom.items() if value > 0.00}
    
    print(f"DICCIONARIO CON VALORES sCDI SON: \n {dicc}")
    print(f"DICCIONARIO CON VALORES sCDI_custom SON: \n {dicc_custom}")
    
    new_row_data = {'zones': indice, 'sCDI': [dicc], 'sCDI_custom': [dicc_custom]}
    new_row = pd.DataFrame(new_row_data)

    sCDI_to_plot = pd.concat([sCDI_to_plot, new_row], ignore_index=True)


print("LOS VALORES DE sCDI A PLOTEAR SON")
#df_sCDI_aux = df_hours[((df_hours["month"].values >= (month_start-1))&(df_hours["month"].values <= (month_end-1)))]
print(sCDI_to_plot)


print(" sCDI CUSTOM VALUES ARE:")
print (indexID)
print (month_start_stop)
print(hour_start_stop)
print (sCDI_custom)



resultados = {
                "zone" : indexID, 
                "custom_month_start-end" : month_start_stop,
                "custom_hour_start-end": hour_start_stop, 
                "cdiSensorFraction": cdiFract,
                "ilum-custom-mean" : ilum_custom_mean,
                "CDI-custom": cdiCustom,
                "custom-sCDI-0lx": custom_sCDI_0lx,
                "custom-sCDI-50lx": custom_sCDI_50lx,
                "custom-sCDI-100lx": custom_sCDI_100lx,
                "custom-sCDI-200lx": custom_sCDI_200lx,
                "custom-sCDI-300lx": custom_sCDI_300lx,
                "custom-sCDI-500lx": custom_sCDI_500lx,
                "custom-sCDI-750lx": custom_sCDI_750lx,
                "custom-sCDI-1000lx": custom_sCDI_1000lx,
                "custom-sCDI-2000lx": custom_sCDI_2000lx,
                "ilum-mean" : ilum_anual_mean,                          
                "CDI": cdi12hs,
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
       
create_file(parameters["CSV_SAVE_PATH"], dfUnificados)




###########################
### GRAPHICS SECTION    ###
###########################

fig = go.Figure()
figs = make_subplots(
    rows=2, cols=2,
    column_widths=[0.7, 0.3], 
    row_heights=[0.5, 0.5], 
    specs=[[{"type": "heatmap", "rowspan": 2}, {"type": "pie"}],
           [None, {"type": "pie"}]])



'''figs = make_subplots(
    rows=1, cols=3,
    column_widths=[0.7, 0.15, 0.15],    
    specs=[[{"type": "heatmap"}, {"type": "pie"}, {"type": "pie"}]])'''

colorbar_setup = dict(
                tickvals = [0, 50, 100, 200, 300, 500, 750, 1000, 2000],
                len = 1,
                tickfont = dict(size = 12),
                x = 0.65
            )

for z in range(len(zones)):
    figs.add_trace(go.Heatmap(
            x=[i for i in range(1, 13)], 
            y=[i for i in range(1, 13)], 
            z=df_to_plot[df_to_plot["zones"]==zones[z]]["mct"].values.reshape((12,12)),
            zmin=0,
            zmax=2000,
            text=df_to_plot[df_to_plot["zones"]==zones[z]]["mct"].values.reshape((12,12)),
            texttemplate="%{text:.2f}",
            name=zones[z],
            colorscale='jet',
            #coloraxis="coloraxis",
            hovertemplate =
                    '<b>Month</b>: %{y}<br>'+
                    '<b>Hour</b>: %{x}<br>'+
                    '<b>Ilum[lux]</b>:<b>%{z:.2f}</b>',
            xgap=1, 
            ygap=1,
            colorbar=colorbar_setup,
            visible=(z==0)),
            row= 1,
            col= 1    
        )
    
for z in range(len(zones)):    
    figs.add_trace(go.Heatmap(
            x=[i for i in range(1, 13)], 
            y=[i for i in range(1, 13)], 
            z=df_to_plot[df_to_plot["zones"]==zones[z]]["cdi"].values.reshape((12,12)),
            zmin=0,
            zmax=2000,
            text=df_to_plot[df_to_plot["zones"]==zones[z]]["cdi"].values.reshape((12,12)),
            texttemplate="%{text:.2f}",
            name=zones[z],
            colorscale='jet',
            #coloraxis="coloraxis",
            hovertemplate =
                    '<b>Month</b>: %{y}<br>'+
                    '<b>Hour</b>: %{x}<br>'+
                    '<b>Ilum[lux]</b>:<b>%{z:.2f}</b>',
            xgap=1, 
            ygap=1,
            colorbar=colorbar_setup,
            visible=False),
            row= 1,
            col= 1    
        )


for z in range(len(zones)):
    figs.add_trace(go.Pie(
        values = list(sCDI_to_plot[sCDI_to_plot["zones"]==zones[z]]["sCDI"].iloc[0].values()),
        labels = list(sCDI_to_plot[sCDI_to_plot["zones"]==zones[z]]["sCDI"].iloc[0].keys()),
        #domain={'x':[0.1,0.5], 'y':[0,0.5]}, 
        hole=0.5,
        direction='clockwise',
        sort=False,
        title = "sCDI Anual",
        showlegend=True,
        visible=(z==0)),
        row= 1,
        col= 2)

for z in range(len(zones)):
    figs.add_trace(go.Pie(
        values = list(sCDI_to_plot[sCDI_to_plot["zones"]==zones[z]]["sCDI_custom"].iloc[0].values()),
        labels = list(sCDI_to_plot[sCDI_to_plot["zones"]==zones[z]]["sCDI_custom"].iloc[0].keys()),
        #domain={'x':[0.1,0.5], 'y':[0,0.5]}, 
        hole=0.5,
        direction='clockwise',
        sort=True,
        title = "sCDI Custom",
        showlegend=False,
        visible=(z==0)),
        row= 2,
        col= 2)


## HEATMAP MASK FOR CUSTOM MONTH AND HOURS SELECTED
predifined_hour_start = int(parameters["HOUR_START"]) + 0.5 - 1
predifined_hour_stop = int(parameters["HOUR_END"]) + 1.5 - 1
predifined_month_start = int(parameters["MONTH_START"]) + 0.5 - 1
predifined_month_stop = int(parameters["MONTH_END"]) + 1.5 - 1
coord = [[1, 1], [13, 13],[1, 1], [13, 13]]
ply_shapes = {}
opacity_value = 0.8
for i in range(0,4):
    ply_shapes['shape_'+str(i)] = go.layout.Shape(type="rect",                                                  
                                                  x0= 0.5,
                                                  x1= 0.5,
                                                  y0= 0.5,
                                                  y1= 0.5,
                                                  line=dict(
                                                    color="gray",
                                                    width=2,
                                                    ),
                                                  fillcolor="gray",
                                                  opacity=opacity_value)

if (month_start > month_end):
    if(hour_start > hour_end):
        buttons_shapes = [
            dict(args=[{'shapes[0].visible': False,
                        'shapes[1].visible': False,
                        'shapes[2].visible': False,
                        'shapes[3].visible': False,                
                        }], 
                label= 'Anual', 
                method='relayout'
                ),
            
            dict(args=[{'shapes[0].visible': True,
                        'shapes[1].visible': True,
                        'shapes[2].visible': True,
                        'shapes[3].visible': False,

                        'shapes[0].x0': 0.5, 
                        'shapes[0].x1': predifined_hour_stop,
                        'shapes[0].y0': predifined_month_stop,
                        'shapes[0].y1': predifined_month_start,

                        'shapes[1].x0': predifined_hour_start,
                        'shapes[1].x1': 12.5,
                        'shapes[1].y0': predifined_month_stop,
                        'shapes[1].y1': predifined_month_start,

                        'shapes[2].x0': predifined_hour_stop,
                        'shapes[2].x1': predifined_hour_start,
                        'shapes[2].y0': 0.5,
                        'shapes[2].y1': 12.5,
                        }], 
                label= 'Predifined', 
                method='relayout'
                )]
    else:        
        buttons_shapes = [
            dict(args=[{'shapes[0].visible': False,
                        'shapes[1].visible': False,
                        'shapes[2].visible': False,
                        'shapes[3].visible': False,                
                        }], 
                label= 'Anual', 
                method='relayout'
                ),
            
            dict(args=[{'shapes[0].visible': True,
                        'shapes[1].visible': True,
                        'shapes[2].visible': True,
                        'shapes[3].visible': False,

                        'shapes[0].x0': 0.5, 
                        'shapes[0].x1': predifined_hour_start,
                        'shapes[0].y0': 0.5,
                        'shapes[0].y1': 12.5,

                        'shapes[1].x0': predifined_hour_stop,
                        'shapes[1].x1': 12.5,
                        'shapes[1].y0': 0.5,
                        'shapes[1].y1': 12.5,

                        'shapes[2].x0': predifined_hour_start,
                        'shapes[2].x1': predifined_hour_stop,
                        'shapes[2].y0': predifined_month_stop,
                        'shapes[2].y1': predifined_month_start,
                        }], 
                label= 'Predifined', 
                method='relayout'
                )]
else:
    if(hour_start > hour_end):
        buttons_shapes = [
            dict(args=[{'shapes[0].visible': False,
                        'shapes[1].visible': False,
                        'shapes[2].visible': False,
                        'shapes[3].visible': False,                
                        }], 
                label= 'Anual', 
                method='relayout'
                ),
            
            dict(args=[{'shapes[0].visible': True,
                        'shapes[1].visible': True,
                        'shapes[2].visible': True,
                        'shapes[3].visible': False,

                        'shapes[0].x0': 0.5, 
                        'shapes[0].x1': 12.5,
                        'shapes[0].y0': 0.5,
                        'shapes[0].y1': predifined_month_start,

                        'shapes[1].x0': 0.5,
                        'shapes[1].x1': 12.5,
                        'shapes[1].y0': predifined_month_stop,
                        'shapes[1].y1': 12.5,             

                        'shapes[2].x0': predifined_hour_start, 
                        'shapes[2].x1': predifined_hour_stop,
                        'shapes[2].y0': predifined_month_start,
                        'shapes[2].y1': predifined_month_stop,
                        }], 
                label= 'Predifined', 
                method='relayout'
                )]
    else:
        buttons_shapes = [
            dict(args=[{'shapes[0].visible': False,
                        'shapes[1].visible': False,
                        'shapes[2].visible': False,
                        'shapes[3].visible': False,                
                        }], 
                label= 'Anual', 
                method='relayout'
                ),
            
            dict(args=[{'shapes[0].visible': True,
                        'shapes[1].visible': True,
                        'shapes[2].visible': True,
                        'shapes[3].visible': True,

                        'shapes[0].x0': 0.5, 
                        'shapes[0].x1': predifined_hour_start,
                        'shapes[0].y0': 0.5,
                        'shapes[0].y1': 12.5,

                        'shapes[1].x0': predifined_hour_stop,
                        'shapes[1].x1': 12.5,
                        'shapes[1].y0': 0.5,
                        'shapes[1].y1': 12.5,             

                        'shapes[2].x0': predifined_hour_start, 
                        'shapes[2].x1': predifined_hour_stop,
                        'shapes[2].y0': 0.5,
                        'shapes[2].y1': predifined_month_start,

                        'shapes[3].x0': predifined_hour_start,
                        'shapes[3].x1': predifined_hour_stop,
                        'shapes[3].y0': predifined_month_stop,
                        'shapes[3].y1': 12.5,
                        }], 
                label= 'Predifined', 
                method='relayout'
                )]

lst_shapes=list(ply_shapes.values())
figs.update_layout(shapes=lst_shapes)

button_layer_metrics_height = -0.15
button_layer_zones_height = -0.15
button_layer_filter_height = -0.3

figs.update_layout(
    autosize=False,
    width=1500,
    height=650,
    margin = dict (t = 0.1, b = 0.5, l = 0, r = 0))

##
##
##
## - MODIFICAR PARA QUE ADOPTE EL PRIMER updatemenus A LOS BOTONES GENERADOS 
## CON EL NUEVO MÉTODO

buttons_plots = []

for i in range(0,len(zones)):
    button_mct = {
        'label': f'{zones[i]} - mct',
        'method': 'restyle',
        'args':[
            {'visible':[i == j or i == j - 2*len(zones) or i == j - 3*len(zones) for j in range(4 * len(zones))]},
            {'title':f'{zones[i]} - mct'}
        ]
    }

    buttons_plots.append(button_mct)

    button_cdi = {
        'label': f'{zones[i]} - CDI',
        'method': 'restyle',
        'args':[
            {'visible':[i == j - len(zones) or i == j - 2*len(zones) or i == j - 3*len(zones) for j in range(4 * len(zones))]},
            {'title':f'{zones[i]} - CDI'}
        ]
    }

    buttons_plots.append(button_cdi)


legend_setup = dict(
    x = 1,
    y = 0.5,
    orientation = "v",
    yanchor = "middle",
    xanchor = "center"
)

figs.update_layout(
    updatemenus=[go.layout.Updatemenu(buttons=buttons_plots,
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
                                        bgcolor="#dadada")],
    legend1=legend_setup,
    legend2=legend_setup
)

figs.update_layout(
    annotations=[
        dict(text="Zones", 
            x=0, xref="paper", 
            y=button_layer_zones_height+0.04, 
            yref="paper",
            align="left", 
            showarrow=False),
        dict(text="Filter", 
            x=0, xref="paper", 
            y=button_layer_filter_height+0.06,
            yref="paper", 
            showarrow=False)
    ])

figs.update_yaxes(
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

figs.update_xaxes(
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

figs.show()

