# -*- coding: utf-8 -*-
"""
Created on Fri May  7 01:49:42 2021
Este script permite obtener datos de la 
pagina de: CFM-ID
@author: RAZC
#SUGERENCIAS:
->MAXIMO 3 pestañas AL TIEMPO en la V4.0.
->Limit exceeded. You are allowed 60 POST requests per minute and 1000 GET requests per second in order to ensure a fair usage 
of this shared resourceLimit exceeded. You are allowed 60 POST requests per minute and 1000 GET requests per second in order
to ensure a fair usage of this shared resource.
"""
#==LIBRERIAS USADAS===========================================================
# libreria propia
import espectros_teoricos as sp_theo
#libreria para generar data frames
import pandas as pd
#libreria para manejar opciones del sistema
import os
# Libreria de scrapping
from selenium import webdriver
from selenium.webdriver.support.ui import Select
#=INGRESO DE DATOS============================================================
# Carga base de datos de excel como data frames
print('Programa para realizar scrapping en el predictor de espectros GC/MS CMF-ID')
n_base=input('¿Desea ingresar el nombre del archivo?\n 1->Si 0->No\n:')
# Seleccion nombre por defecto "metabolite_match_DB.csv"
if n_base=='1':
    n_base=input(' Ingrese el nombre de la base de datos\n Ejemplo-->metabolite_match_DB.xlsx o metabolite_match_DB.csv \n:')
else:
    n_base='metabolite_match_DB.csv'
if '.xlsx'in n_base:
    base_datos= pd.read_excel(n_base)
else:
    base_datos= pd.read_csv(n_base)
n_ver=input('\nSeleccione la versión del CFM-ID \n0-> V2.0 1-> V3.0 2-> V4.0\n:')    
version={'0':'http://cfmid2.wishartlab.com/predict',
         '1':'http://cfmid.wishartlab.com/predict',
         '2':'http://cfmid4.wishartlab.com/predict'}
page = version.get(n_ver)
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
# Generando nombres de los archivos 
Nombres_archivos={};acum=0
# Smile asociado al tipo de origen
S_tipo={}
for k in range(len(Tipo_de_origen)):  
    Nombre=[];cod_smile=[]
    df_origen=base_datos.copy()
    filtro=df_origen[df_origen["origen"]==Tipo_de_origen[k]]
    # Selecciona la codificacion PubChem 
    Pubchem=filtro["PubChem"]
    df_smiles=filtro["SMILES"]
    for i in range(Cantidad_tipos.iloc[k]):
        # Concatenando listas nombre de archivo 
        # Se codifican asi: PubChem_op_N°
        cod=str(Pubchem.iloc[i])
        cod=cod.replace(".0","")
        Nombre.append(cod+"_op_"+str(i+1))
        # smile asociado
        cod_smile.append(df_smiles.iloc[i])
    Nombres_archivos.update({str(Tipo_de_origen[k]):Nombre})
    S_tipo.update({str(Tipo_de_origen[k]):cod_smile})
#=SELECCION DE ADUCTOS========================================================
rango=0.2 # incertidumbre en la masa
aductos,lista_aduc_dict,dict_dF=sp_theo.aductos(base_datos,Tipo_de_origen,rango)
#=CREACION DE CARPETAS========================================================
# lista de aductos que simula el CFM-ID
adducts_p={"[M+H]+":'mh',"[M]+":'m_p',"[M+NH4]+":'m_nh4',
           "[M+Na]+":'m_na',"[M+K]+":'m_k',"[M+Li]+":'m_li',"Unknown":'u'}
adducts_keys=list(adducts_p.keys())
rta=2
ubi='Resultados' # carpeta de ubicación resultados
if os.path.exists(ubi)==False:
    os.mkdir(ubi)
while rta>0:
    os.system ("cls")
    print('Tipo de origenes y cantidad de cada tipo')
    print(Cantidad_tipos)
    Tipo_S=input("Escriba el tipo de origen: ")
    if Tipo_S[-1]=='0':
        Tipo_S=Tipo_S[0:len(Tipo_S)-1]
    smiles=S_tipo.get(Tipo_S)
    df_aducto=dict_dF[str(Tipo_S)]
    pre_aducto=1
    if rta==2:
        # navegador
        driver=webdriver.Firefox(executable_path="geckodriver.exe")  
    while pre_aducto>0:
        # lista resultados positivos o fallidos
        completado_lis=[];fallo_lis=[]
        url=[] ;lis_aduct_simu=[]    
        seleccion='0'
        k=0;cant_tab=1    
        while k <(len(smiles)):
            if k==0:
                # Primer click submit envio de datos
                print('\n Tipo de origen: '+Tipo_S)
                print('\n Candidatos vs Aductos asociados a cada opción')
                # Tipo de aducto
                # Clasificación de aductos    
                print('\n',df_aducto)
                print('\n Lista de aductos de modo ion positivos que simula CFM-ID')
                print('\n Número de aducto:',list(range(1,8)))
                print('\n Tipo de aducto:',list(adducts_p.keys()))
                adducts=int(input('\n Escriba el número correspondiente al tipo de aducto: '))-1
                adducts=adducts_keys[adducts]
                # seleccion aducto cfm-id
                if len(smiles)>1:
                    indiv_smile=input('¿Desea simular todos los candidatos? 1->Si 0->No\n:')
                    if indiv_smile=='1':
                        print('\n ¿Desea usar este aducto automaticamente para toda la simulación?')
                        seleccion=input('1-> Si 0-> No \n: ')
                    else:
                        agre=1
                        print('\n ¿Desea usar este aducto automaticamente para toda la simulación?')
                        seleccion=input('1-> Si 0-> No \n: ')
                        while agre>0:
                            lis_aduct_simu.append(int(input('\nIngrese el número del candidato:'))-1)
                            agre=int(input('\nDesea ingresar otro candidato 1->Si 0->No\n:'))
                else:
                    indiv_smile='0'
                    
               #---Trabajo Bot------------------------------------------------------------
            if indiv_smile=='1':
                sp_theo.scrap(driver,page,k,smiles,adducts)
                # creacion de multiples pestañas
                if (len(smiles)>1)&(seleccion=='1'):
                    if k==0:
                        mult_tab=input('¿Desea utilizar multiples pestañas? 1->Si 0->No\n:')
                        if mult_tab=='1':
                            cant_tab=int(input('¿Cuantas pestañas?\n:'))
                    if cant_tab>abs(k-len(smiles)):
                        cant_tab=abs(k-len(smiles))
                    for j in range(1,cant_tab):
                        # cargar pagina 
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[j])
                        R=k+j
                        sp_theo.scrap(driver,page,R,smiles,adducts)
            else:
                if len(smiles)>1:
                    r=lis_aduct_simu[k]
                else:
                    r=k
                sp_theo.scrap(driver,page,r,smiles,adducts)
                if (len(lis_aduct_simu)>1)&(seleccion=='1'):
                    mult_tab=input('¿Desea utilizar multiples pestañas? 1->Si 0->No\n:')
                    if mult_tab=='1':
                        cant_tab=int(input('¿Cuantas pestañas?\n:'))
                    if cant_tab>abs(k-len(lis_aduct_simu)):
                        cant_tab=abs(k-len(lis_aduct_simu))
                    for j in range(cant_tab):
                        r=lis_aduct_simu[j]                
                        # abrir una nueva pestaña
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[j])
                        sp_theo.scrap(driver,page,r,smiles,adducts)
            if cant_tab>1|k==0:
                A=input("\n Presione Enter para continuar")           
            os.system ("cls")
            print("\n Origen "+Tipo_S)
            print('\nCandidatos vs Aductos asociados a cada opción')
            print('\n',df_aducto)
            if (len(smiles)>1)&(cant_tab>1):
                for j in range(cant_tab):
                    K=k+j
                    driver.switch_to.window(driver.window_handles[0])
                    print('Candidatos '+str(K+1)+' de '+str(len(smiles)))
                    guardar=input('\n1-> Guarda el resultado \n0-> continuar \n: ')
                    if guardar=='1':
                        # Pagina de resultados
                        # Link descarga resultado
                        next_1=driver.find_element_by_class_name('btn-download')
                        next_1.click()
                        url.append(str(driver.current_url))
                        completado_lis.append(str(K+1))
                    else:
                        url.append('fallo')
                        fallo_lis.append(str(K+1))
                    if (j+1)<cant_tab:
                        driver.close()
                k=k+cant_tab
            elif (indiv_smile=='0')&(len(smiles)>1):
                print('Candidatos '+str(lis_aduct_simu[k]+1)+' de '+str(len(smiles)))
                guardar=input('\n1-> Guarda el resultado \n0-> continuar \n: ')
                if guardar=='1':
                    # Pagina de resultados
                    # Link descarga resultado
                    next_1=driver.find_element_by_class_name('btn-download')
                    next_1.click()
                    url.append(str(driver.current_url))
                    completado_lis.append(str(k+1))
                else:
                    url.append('fallo')
                    fallo_lis.append(str(k+1))
                break
            else:
                print('Candidatos '+str(k+1)+' de '+str(len(smiles)))
                guardar=input('\n1-> Guarda el resultado \n0-> continuar \n: ')
                if guardar=='1':
                    # Pagina de resultados
                    # Link descarga resultado
                    next_1=driver.find_element_by_class_name('btn-download')
                    next_1.click()
                    url.append(str(driver.current_url))
                    completado_lis.append(str(k+1))
                else:
                    url.append('fallo')
                    fallo_lis.append(str(k+1))
                k=k+1
#---- pagina de descarga de resultados----------------------------------------
        # las paginas pueden sufrir caidas por el certificado
        if completado_lis==[]:
            lista_R='0'
        else:
            # se una crea carpeta para el origen
            direc=ubi+'/'+Tipo_S
            if os.path.exists(direc)==False:
                os.mkdir(direc)
            # se guarda el Archivo .csv final en esa carpeta
            lista_R=completado_lis
            # Nombre del archivo Final
            name=Nombres_archivos.get(Tipo_S)
            for i in range(len(url)):
                if indiv_smile=='1':
                    if url[i]!='fallo':
                        archivo=sp_theo.url_to_csv(url[i],direc+'/'+name[i]+'_'+adducts_p[adducts])
                else:
                    r=lis_aduct_simu[i]
                    if url[i]!='fallo':
                        archivo=sp_theo.url_to_csv(url[r],direc+'/'+name[r]+'_'+adducts_p[adducts])                
        if fallo_lis==[]:
            Fallo_R='0'
        else:
            Fallo_R=fallo_lis
        os.system ("cls")
        print('Resultados')            
        print('\nTipo de origen '+Tipo_S+'\nCandidatos')
        print('\nRealizados \n',lista_R)
        print('\nFallidos \n',Fallo_R)
        pre_aducto=int(input('\n ¿Desea utilizar otro aducto?: 1->Si 0->No\n:'))
        rta=pre_aducto
    rta=int(input('\n¿Desea continuar con otro origen?: 1->Si 0->No\n: '))
    if rta==0:
        os.system ("cls")
        print('Gracias')
        driver.close()
        break
