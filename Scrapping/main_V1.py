# -*- coding: utf-8 -*-
"""
Created on Fri May  7 01:49:42 2021
Este script permite obtener datos de la 
pagina de:
http://cfmid2.wishartlab.com/predict    --->Versión 2.0
https://cfmid.wishartlab.com/predict    --->Versión 3.0      
http://cfmid4.wishartlab.com/predict    --->Versión 4.0
@author: RAZC
"""
#==LIBRERIAS USADAS===========================================================
# libreria propia
import espectros_teoricos_V1 as sp_theo
#libreria para generar data frames
import pandas as pd
#libreria para manejar opciones del sistema
import os
# Libreria de scrapping
from selenium import webdriver
#=INGRESO DE DATOS============================================================
# Carga base de datos de excel como data frames
n_base=input(' Ingrese el nombre de la base de datos\n Ejemplo-->BD_principal.xlsx \n:')
base_datos= pd.read_excel(n_base)
page = 'https://cfmid.wishartlab.com/predict'
#=RUTINA PRINCIPAL============================================================
# Clasificiacion de los Tipos de origen
Cantidad_tipos=base_datos["origen"].value_counts() 
Tipo_de_origen=list(Cantidad_tipos.index)
# Selecciona la codificacion PubChem 
Pubchem=base_datos["PubChem"]
# Generando nombres de los archivos 
Nombres_archivos={};acum=0
# Smile asociado al tipo de origen
S_tipo={}
for k in range(len(Tipo_de_origen)):  
    Nombre=[];cod_smile=[]
    for i in range(Cantidad_tipos.iloc[k]):
        # Concatenando listas nombre de archivo 
        # Se codifican asi: PubChem_op_N°
        cod=str(Pubchem.iloc[acum])
        cod=cod.replace(".0","")
        Nombre.append(cod+"_op_"+str(i))
        # smile asociado
        cod_smile.append(base_datos["SMILES"].iloc[acum])
        acum=acum+1 # acumulador posicion del pubchem
    Nombres_archivos.update({str(Tipo_de_origen[k]):Nombre})
    S_tipo.update({str(Tipo_de_origen[k]):cod_smile})
print('Tipo de origenes y cantidad de cada tipo')
print(Cantidad_tipos)
rta=1
ubi='Resultados' # carpeta de ubicación resultados
os.mkdir(ubi)
while rta>0:
    # Recuerde que si termina en cero despues del punto decimal
    # debe omitirlo ejemplo 1.20 seria 1.2
    Tipo_S=input("Escriba el tipo de origen: ")
    smiles=S_tipo.get(Tipo_S)
    url=[]
    #---Trabajo Bot------------------------------------------------------------
    # navegador
    driver=webdriver.Firefox(executable_path="geckodriver.exe")
    for k in range(len(smiles)):
        # pagina de ingreso de smiles
        # cargar pagina
        driver.get(page)        
        input_smile=driver.find_element_by_name("predict_query[compound]")
        input_smile.send_keys(smiles[k])
        os.system ("cls")
        #primer click submit envio de datos
        A=input("Presione Enter para continuar")
        next_1=driver.find_element_by_name("commit").click()
        os.system ("cls")
        print('Origen '+Tipo_S+' opción '+str(k+1)+' de '+str(len(smiles))+'\n')
        guardar=input(' 1-> Guarda el resultado \n 0-> continuar \n: ')
        if guardar=='1':
            # Pagina de resultados
            # Link descarga resultado
            next_1=driver.find_element_by_class_name('btn-download')
            next_1.click()
            url.append(str(driver.current_url))
        else:
            url.append('fallo')
    # se una crea carpeta para el origen
    direc=ubi+'/'+Tipo_S
    os.mkdir(direc)
    # se guarda el Archivo .csv final en esa carpeta
    # pagina de descarga de resultados
    # las paginas pueden sufrir caidas por el certificado
    # Nombre del archivo Final
    name=Nombres_archivos.get(Tipo_S)
    for i in range(len(url)):
        if url[i]!='fallo':
            archivo=sp_theo.url_to_csv(url[i],direc+'/'+str(name[i]+1))
    os.system ("cls")
    rta=int(input('Desea continuar: 1->Si 0->No\n: '))
    if rta==0:
        os.system ("cls")
        print('Gracias')
        driver.close()
        break





