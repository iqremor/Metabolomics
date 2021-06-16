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
from selenium.webdriver.support.ui import Select
#=INGRESO DE DATOS============================================================
# Carga base de datos de excel como data frames
n_base=input(' Ingrese el nombre de la base de datos\n Ejemplo-->metabolite_match_DB.xlsx o metabolite_match_DB.csv \n:')
if '.xlsx'in n_base:
    base_datos= pd.read_excel(n_base)
else:
    base_datos= pd.read_csv(n_base)
page = 'https://cfmid.wishartlab.com/predict'
#=FILTRADO DE DATOS ORIGENES A SIMULAR========================================
# carga de origenes experimentales 
origenes_exp=pd.read_csv("Mass_final.csv")
# origenes teoricos que  coinciden
origenes_theo=pd.DataFrame({'mass':list(base_datos["origen"])})
# combinación entre los experimentales y teoricos
origenes_final=origenes_exp.merge(origenes_theo,how='inner',indicator='union')
# origenes que coincidieron entre experimentales y teoricos para iniciar simulación
origenes_final=origenes_final[(origenes_final['union']=='both')]
origenes_final=origenes_final.rename(columns={'mass':'origen'})
origenes_final=origenes_final.drop(['union'],axis=1)
#=RUTINA PRINCIPAL============================================================
# Clasificiacion de los Tipos de origen
Cantidad_tipos=origenes_final["origen"].value_counts() 
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
        Nombre.append(cod+"_op_"+str(i+1))
        # smile asociado
        cod_smile.append(base_datos["SMILES"].iloc[acum])
        acum=acum+1 # acumulador posicion del pubchem
    Nombres_archivos.update({str(Tipo_de_origen[k]):Nombre})
    S_tipo.update({str(Tipo_de_origen[k]):cod_smile})

#=SELECCION DE ADUCTOS========================================================
aductos=base_datos.copy()
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
    rango=0.2 # incertidumbre en la masa
    Tp_omax=Tp_o+rango;Tp_omin=Tp_o-rango
    dict_aduct=dict_dF[str(Tp_o)]
    for j in range(1,len(cols_aductos)):
        cols=cols_aductos[j]; 
        dict_o=dict_aduct[str(cols)]
        filtro=dict_o[(dict_o<=Tp_omax)&(dict_o>=Tp_omin)]
        if filtro.size!=0:
            aduct_o.update({str(cols):len(filtro)})
    # lista de aductos con peso molecular cercanos al origen
    lista_aductos=list(aduct_o.keys())
    lista_aduc_dict.update({str(Tp_o):lista_aductos}) 
#=CREACION DE CARPETAS========================================================
rta=2
ubi='Resultados' # carpeta de ubicación resultados
if os.path.exists(ubi)==False:
    os.mkdir(ubi)
while rta>0:
    os.system ("cls")
    print('Tipo de origenes y cantidad de cada tipo')
    print(Cantidad_tipos)
    # Recuerde que si termina en cero despues del punto decimal
    # debe omitirlo ejemplo 1.20 seria 1.2
    Tipo_S=input("Escriba el tipo de origen: ")
    if Tipo_S[-1]=='0':
        Tipo_S=Tipo_S[0:len(Tipo_S)-1]
    smiles=S_tipo.get(Tipo_S)
    url=[] 
    # lista resultados positivos
    lista_result={};fallo={}
    # lista de aductos que simula el CFM-ID
    adducts_p="[M+H]+","[M]+","[M+NH4]+","[M+Na]+","[M+K]+","[M+Li]+","Unknown"
    adducts_n="[M-H]-","[M]-","[M+Cl]-","[M+HCOOH-H]-","[M+CH3COOH-H]-","[M-2H]2-","Unknown"
    seleccion='0'
    #---Trabajo Bot------------------------------------------------------------
    # navegador
    if rta==2:
        driver=webdriver.Firefox(executable_path="geckodriver.exe")  
    for k in range(len(smiles)):
        # pagina de ingreso de smiles
        # cargar pagina
        driver.get(page)
        input_smile=driver.find_element_by_name("predict_query[compound]")
        input_smile.send_keys(smiles[k])
        os.system ("cls")
        if k==0:
            print('\n Lista de aductos que simula CFM-ID')
            print('\n postivos:',adducts_p)
            print('\n negativos:',adducts_n)
            # Primer click submit envio de datos
            print('Tipo de origen: '+Tipo_S)
            print('\n Opciones vs Aductos asociados a cada opción')
            # Tipo de aducto
            # Clasificación de aductos    
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
            print('\n',df_aducto)
        # seleccion aducto cfm-id
        Elemento=driver.find_element_by_id("predict_query_adduct_type")
        drp=Select(Elemento)
        if seleccion=='0':
            adducts=input('\n Escriba el tipo de aducto:')
            if len(smiles)>1:
                print('\n ¿desea usar este aducto automaticamente para toda la simulación?')
                seleccion=input('1-> Si 0-> No \n: ')
        drp.select_by_visible_text(adducts)
        if k==0:
            A=input("\n Presione Enter para continuar")
        next_1=driver.find_element_by_name("commit").click()
        os.system ("cls")
        print('Origen '+Tipo_S+' opción '+str(k+1)+' de '+str(len(smiles)))
        print('\nOpciones vs Aductos asociados a cada opción')
        print('\n',df_aducto)
        guardar=input('\n1-> Guarda el resultado \n0-> continuar \n: ')
        if guardar=='1':
            # Pagina de resultados
            # Link descarga resultado
            next_1=driver.find_element_by_class_name('btn-download')
            next_1.click()
            url.append(str(driver.current_url))
            lista_result.update({Tipo_S:str(k+1)})
        else:
            url.append('fallo')
            fallo.update(({Tipo_S:str(k+1)}))
    # pagina de descarga de resultados
    # las paginas pueden sufrir caidas por el certificado
    if lista_result=={}:
        lista_R='0'
    else:
        # se una crea carpeta para el origen
        direc=ubi+'/'+Tipo_S
        if os.path.exists(direc)==False:
            os.mkdir(direc)
        # se guarda el Archivo .csv final en esa carpeta
        lista_R=list(lista_result.get(Tipo_S))
        # Nombre del archivo Final
        name=Nombres_archivos.get(Tipo_S)
        for i in range(len(url)):
            if url[i]!='fallo':
                archivo=sp_theo.url_to_csv(url[i],direc+'/'+name[i])
    if fallo=={}:
        Fallo_R='0'
    else:
        Fallo_R=list(fallo.get(Tipo_S))
    os.system ("cls")
    print('Resultados\n')            
    print('Tipo de origen '+Tipo_S+'\nopciones')
    print('\nPositivas \n',lista_R)
    print('\nFallidas \n',Fallo_R)
    rta=int(input('\nDesea continuar: 1->Si 0->No\n: '))
    if rta==0:
        os.system ("cls")
        print('Gracias')
        driver.close()
        break





