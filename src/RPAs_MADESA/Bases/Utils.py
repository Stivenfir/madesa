####################################################################################################################
# HERRAMIENTAS BASE QUE NECESITA EL RPOYEXTO                                                                       #
# 1. macrovega.json  ::  Este archivo contiene informacióin de todos los departamentos y ciudades principales (COL)#
#    -El archivo se puede descargar en...                                                                          #
#        https://raw.githubusercontent.com/marcovega/colombia-json/master/colombia.min.json                        #
#    -Recuerda editar el archivo (TODO EN MAYUSCULAS Y QUITAR LAS TILDE)                                           #
#                                                                                                                  #
# 1. def CrearMacrovega(): #Esto crea una tabla con departamentos y municipios (si es necesario tambien crea la BD)#
#    -Ejecutar esta funcion si se pierde la tabla                                                                  #
#    -Esta tabla usa el archivo "macrovega.json" guardada en la carpeta JSON                                       #
#    -Descomenta o llama la funcion "CrearMacrovega()" para comenzar la creación de la tabla                       # 
####################################################################################################################

import os
import sys
import pyodbc
import sqlite3
import requests
import traceback
import numpy as np
from tqdm import tqdm
from json import load
from json import dumps
from json import loads
from time import sleep
from decimal import Decimal

PATH_root = os.path.join(sys.path[-1],"RPAs_MADESA")
PATH_txt  = os.path.join(PATH_root,"TXT")
PATH_html = os.path.join(PATH_root,"HTML")
PATH_json = os.path.join(PATH_root,"JSON")
PATH_bd   = os.path.join(PATH_root,"BDs")
PATH_xls  = "\\\\172.16.10.40\\Consultas1\\Seguimientos madesa 2026.xlsx"

LoG=open(os.path.join(PATH_txt,"LOG.txt"),'w',encoding="utf-8")

server = '172.16.10.54\\DBABC21' # 'serverName\instanceName,port' # to specify an alternate port
username = 'Operativo'# 'myusername' 
password = 'Repecev2019*' # 'mypassword' 
DataBase = 'LAB'

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+DataBase+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

cnxnLite   = sqlite3.connect(os.path.join(PATH_bd,"InfoLocal.db"))
cursorLite = cnxnLite.cursor()
cnxnLite.execute("PRAGMA foreign_keys = ON")

cursorLite.execute("SELECT * FROM municipios")
Mnpios=cursorLite.fetchall()
cursorLite.execute("SELECT * FROM SharePoint_CheckPoint")
V_Graph=cursorLite.fetchone() #[id,NombreLista,token,url]
Cabecera={"Authorization": f"Bearer " + V_Graph[2]}
D_Volaces={"Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U"}

def GraphPet(url,Cabecera):
    Rta=requests.get(url, headers=Cabecera)
    return Rta.json()

def SaveHTML(NmeA,contenido=""):
    if not contenido:
        return False
    else:
        with open(os.path.join(PATH_html,f"{NmeA}.html"),'w',encoding="utf-8") as A:
            A.write(contenido)
            return True

def CrearMacrovega(): #Esto crea una tabla con departamentos y municipios (si es necesario tambien crea la BD)
    
    cnxnLite.execute("CREATE TABLE IF NOT EXISTS departamentos (id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL UNIQUE)")
    cnxnLite.execute("CREATE TABLE IF NOT EXISTS municipios (id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL,departamento_id INTEGER NOT NULL,FOREIGN KEY (departamento_id) REFERENCES departamentos(id))")
    
    A=open(os.path.join(PATH_json,"macrovega.json"), "r", encoding="utf-8")
    Datos = load(A)
    A.close()
    for Info in Datos:
        cursorLite.execute("INSERT OR IGNORE INTO departamentos (nombre) VALUES (?)",(Info["DEPARTAMENTO"],))
    cnxnLite.commit()
    for Info in Datos:
        cursorLite.execute("SELECT id FROM departamentos WHERE nombre = ?",(Info["DEPARTAMENTO"],))
        Depto_id = cursorLite.fetchone()[0]
        for Ciudad in Info["CIUDADES"]:
            cursorLite.execute("INSERT INTO municipios (nombre, departamento_id) VALUES (?, ?)",(Ciudad,Depto_id))
    cnxnLite.commit()
    cnxnLite.close()

    print("Base de datos creada correctamente.")

def SQLpet1(Transportadora="ENVIA"):#Petición dedicada a traer de la base de datos la mercancia de MADESA y en entregarla en un JSON
    D=[]
    cursorLite.execute("SELECT * FROM InfoPedidos WHERE Transportadora=? AND (GUIA IS NULL OR LENGTH(Guia)<4) ORDER BY id ASC",(str(Transportadora.upper()),))
    #cursor.execute("SELECT * FROM WMS_GENERACION_GUIAS_MADESA WHERE DiceContener IN ('3227166502')")
    Llaves=[V[0] for V in cursorLite.description]
    L=len(Llaves)
    for F in cursorLite.fetchall():
        D.append({Llaves[i]:F[i] for i in range(0,L)})
    return D

def SQLpet2(V_SKUHijos):#los SKU-Hijos son los articulos, se entrega la información de todos los articulos a trabajar

    V_SKUs=[]#1. Organizar todos los SKU en una lista
    if not V_SKUHijos or not isinstance(V_SKUHijos, list):
        V_SKUs=[str(V_SKUHijos)]
    else:
        for grupo in V_SKUHijos:
            V=grupo.split(",")
            for X in V:
                V_SKUs.append(X)
    Interrogantes = ','.join('?' for _ in V_SKUs)#Consultar la información de los SKU's en cuestión
    cursor.execute(f"SELECT * FROM MADESA_SKUHijo WHERE Hijo in ({Interrogantes})",V_SKUs)
    M=cursor.fetchall()
    L=len(M)
    return {#Se regresa un Dic con vectores NP para futuras operaciones
        "Hijo":np.array([M[i][0] for i in range(0,L)],dtype='U'),
        "EAN":np.array([M[i][2] for i in range(0,L)],dtype='U'),
        "Ancho_cm":np.array([int(M[i][3]*1000) for i in range(0,L)],dtype=np.uint64),#Los arreglo se magnificarn x1000 para mejorar la precicion en las operaciones
        "Alto_cm":np.array([int(M[i][4]*1000) for i in range(0,L)],dtype=np.uint64),
        "Largo_cm":np.array([int(M[i][5]*1000) for i in range(0,L)],dtype=np.uint64),
        "Peso":[int(M[i][6]*1000) for i in range(0,L)],
        "Valor":[int(M[i][7]*1000) for i in range(0,L)]
    }

def SQLpet3(Transportadora="ENVIA"):
    cursorLite.execute("SELECT * FROM InfoPedidos WHERE Guia IS NOT NULL AND Transportadora=? ORDER BY idSharePoint DESC",(Transportadora,))
    resultado=cursorLite.fetchall()
    Cabeceras = [col[0] for col in cursorLite.description]
    D=[]
    L=len(Cabeceras)
    for F in resultado:
        D.append({Cabeceras[i]:F[i] for i in range(0,L)})
    return dumps({"data":D},ensure_ascii=False,default=str)

def subSTR(S,Desde='',Hasta=''):
    S1 = S[S.find(Desde):]
    S=S1  if Hasta=='' else S1[:S1.find(Hasta)]
    return S

def SoloDigitos(S,Desde='',Hasta='',b=0):
    S1 = subSTR(S,Desde=Desde,Hasta=Hasta) if Desde!='' or Hasta!='' else S
    return ''.join(s for s in S1 if s.isdigit())

def InfoDepto(s=""):
    if s=="":
        return ['','']
    else:
        S=s.upper()
        #1. REVISAR SI UNA DE LAS CIUDADES DE LA BD SE ENCUENTRA DENTRO DE [S]
        L=0
        V=[]
        for v in Mnpios:
            l=len(v[1])
            if v[1] in S and l>=L:
                cursorLite.execute("SELECT nombre FROM departamentos WHERE id=?",(v[2],))
                V=[cursorLite.fetchone()[0],v[1],v[2],v[0]]
                L=l
        if len(V)>1:
            return V
        elif "BOGOTA" in S:#2. SI EL PASO 1 NO SIRVE....
            V=["CUNDINAMARCA","BOGOTA",13,495]
        elif "SOACHA" in S:
            V=["CUNDINAMARCA","SOACHA",573,13]
        elif "CARTAGENA" in S:
            V=["BOLIVAR","CARTAGENA DE INDIAS",5,167]
        elif "BARRANQUILLA" in S:
            V=["ATLANTICO","BARRANQUILLA",4,136]
        elif " CALI " in S or " CALI " in S or " CALI." in S or "CALI " in S:
            V=["VALLE DEL CAUCA","CALI",30,1065]
        else:
            V=['','',0,0]
        return V


Sesion=requests.session()
#CrearMacrovega()