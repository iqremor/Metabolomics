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
def aductos(df,Tipo_de_origen,rango):
    # Esta funcion selecciona los aductos y crea un data frame por cada aducto
    # donde se incluyen sus candidatos
    aductos=df.copy()
    aductos=aductos.drop(['Unnamed: 0', 'Names', 'Chemical.Formula',
                          'Monoisotopic.Molecular.Weight', 'SMILES', 'PubChem',
                          'Molecular.Weight'],axis=1)
    cols_aductos=['origen','M.H', 'X.M.2H.', 'M.Na', 'M.K', 'M.NH4', 'M.H.H2O', 'M.3H', 'M.2H.Na',
           'M.H.2Na', 'M.3Na', 'M.H.NH4', 'M.H.Na', 'M.H.K', 'M.ACN.2H', 'M.2Na',
           'M.2ACN.2H', 'M.3ACN.2H', 'M.CH3OH.H', 'M.ACN.H', 'M.2Na.H',
           'M.Isoprop.H', 'M.ACN.Na', 'M.2K.H', 'M.2ACN.H', 'M.Isoprop.Na.H',
           'X2M.H', 'X2M.NH4', 'X2M.Na', 'X2M.K', 'X2M.ACN.H', 'X2M.ACN.Na',
           ]
    aductos=aductos[cols_aductos]
    # Clasificación de origenes y sus respectivos aductos
    dict_dF={}; lista_aduc_dict={}
    for i in range(len(Tipo_de_origen)):
        Tp_o=Tipo_de_origen[i]
        filtro=aductos[aductos["origen"]==Tp_o]
        dict_dF.update({str(Tp_o):filtro})
    # seleccion aducto mas cercano al origen
        aduct_o={}
        Tp_omax=Tp_o+rango;Tp_omin=Tp_o-rango
        dict_aduct=dict_dF[str(Tp_o)]
        for j in range(1,len(cols_aductos)):
            cols=cols_aductos[j] 
            dict_o=dict_aduct[str(cols)]
            filtro=dict_o[(dict_o<=Tp_omax)&(dict_o>=Tp_omin)]
            if filtro.size!=0:
                aduct_o.update({str(cols):len(filtro)})
        # lista de aductos con peso molecular cercanos al origen
        lista_aductos=list(aduct_o.keys())
        lista_aduc_dict.update({str(Tp_o):lista_aductos})
        filtro=clasf_aductos(str(Tp_o),cols_aductos,lista_aduc_dict,rango,dict_dF)
        dict_dF.update({str(Tp_o):filtro})
    return aductos,lista_aduc_dict,dict_dF
    
def clasf_aductos(Tipo_S,cols_aductos,lista_aduc_dict,rango,dict_dF):
    #Esta funcion genera un dataframe con los aductos especificos de cada masa 
    # en el rango determinado
     diferencia=list(set(cols_aductos).difference(set(lista_aduc_dict.get(Tipo_S))))
     df_aducto=dict_dF.get(Tipo_S)
     df_aducto=df_aducto.drop(diferencia,axis=1)
     Tp_max=float(Tipo_S)+rango;Tp_min=float(Tipo_S)-rango
     lista_aducto_p=lista_aduc_dict.get(Tipo_S)
     for i in range(len(lista_aducto_p)):
         aduc_l=lista_aducto_p[i]
         df_aducto.loc[(df_aducto[aduc_l]>Tp_max)|(df_aducto[aduc_l]<Tp_min),aduc_l] = ''
     df_aducto=df_aducto.reset_index()
     df_aducto=df_aducto.drop('index',axis=1)
     return df_aducto
 
def scrap(driver,page,k,smiles,adducts):
    # esta función permite cargar la pagina  el aducto y da click para iniciar la simulación
    # cargar pagina
    driver.get(page)
    input_smile=driver.find_element_by_name("predict_query[compound]")
    input_smile.send_keys(smiles[k])
    # seleccionar aducto
    Elemento=driver.find_element_by_id("predict_query_adduct_type")
    drp=Select(Elemento)
    drp.select_by_visible_text(adducts)
    # click para cargar la pagina 
    next_1=driver.find_element_by_name("commit").click()
