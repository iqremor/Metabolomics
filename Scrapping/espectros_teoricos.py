# -*- coding: utf-8 -*-
"""
Created on Fri May  7 01:47:14 2021
Libreria de funciones para obtener datos de  
la pagina de https://cfmid.wishartlab.com/
@author: RAZC
"""
#==LIBRERIAS USADAS===========================================================
# Scrapping
import requests
import urllib3 
from bs4 import BeautifulSoup
# Manejo de datos
import pandas as pd
from io import StringIO
#==FUNCIONES UTILIZADAS=======================================================
def fun(nc):
    # esta función separa por espacios un columna de un dataframe
    nc_l=list(nc)# lista 
    elemento=[]; eV=[]; xeV=[]
    for i in range(len(nc_l)):
        elemento=nc_l[i].split(" ")
        eV.append(elemento[0])
        xeV.append(elemento[1])
    dic_energy={'eV':eV,'xeV':xeV}
    df = pd.DataFrame(dic_energy, columns = ['eV','xeV'])
    return df

def url_to_csv(pagina,name):
    # Captura de datos "Scrapping"
    urllib3.exceptions.InsecureRequestWarning()
    urllib3.exceptions.SSLError()#Excepción de certificado de pagina
    page_result = requests.get(pagina,verify=False) 
    soup= BeautifulSoup(page_result.content,'lxml')
    # convierte los datos en tipo string
    datos=soup.p.text
    limpieza=datos.split("\n0") # separar los datos energy{0,1 y 2}
    var=limpieza[0]
    # limpieza adicional
    if var.find('In-silico')==1:
            limpieza=var.split("energy0") # separar los datos energy{0,1 y 2}
            var=limpieza[1]
            var='energy0'+var
    # Convierte los datos a un data frame
    T_datos=StringIO(var)
    df=pd.read_csv(T_datos)
    # Arreglo del data frame "filtrado"
    # Busca las palabras clave en el data frame
    val=list((df['energy0']=='energy1')|(df['energy0']=='energy2'))
    # Encuentra la posición de las palabras clave
    pos=[i for i in range(0,len(val)) if val[i]==True]
    # Nombres de columnas
    T=["10eV","10xeV","20eV","20xeV","40eV","40xeV",]
    Archivo_final=pd.DataFrame(columns=T)
    # Separar en columnas
    col=list(df["energy0"]) # columna principal df
    # Columnas separadas
    if pos==[]: # caso 1 energia
        nc=col
    elif len(pos)==1: #caso 2 energias
        nc=[col[:pos[0]],col[pos[0]+1:]]
    elif len(pos)==2: # caso 3 energias
        nc=[col[:pos[0]],col[pos[0]+1:pos[1]],col[pos[1]+1:]]
    dict_af={}
    for i in range(len(pos)+1):
        df=fun(nc[i])
        dict_af.update({str(i):df})
    # uniendolas
    Archivo_final=pd.concat([dict_af['0'],dict_af['1'],dict_af['2']],axis=1)  
    Archivo_final.to_csv(name+'.csv',encoding='utf-8',index=False,header=True,sep=(';'))
    return 
