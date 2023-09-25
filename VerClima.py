#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 23:10:16 2015

@author: Joel y Belén
"""


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.collections import LineCollection
import subprocess

#En donde se encuentran los archivos del clima
path_cloudwatcher='./DatosClima/CloudWatcher.csv'
path_datos='./DatosClima/'

#Define los colores del grafico
color_ambiente='r'
color_dew='green'
color_viento='b'
color_humedad='violet'
color_nublado='y'
color_overcast='r'

#%%
##Pregunta de que fecha se quieren mirar los datos del clima, revisa la fecha de la computadora (esto es un comando que se tira en la terminal de linux)
##En base a eso decide y define unos parametros
# intro=raw_input('Datos climaticos de que dia(ddmm-YYYY)? ')


# hoy=subprocess.check_output('date +%d%m-%Y',shell=True).replace('\n','')
# ayer=subprocess.check_output('date --date="-1 day" +%d%m-%Y',shell=True).replace('\n','')
# hora=subprocess.check_output('date +%H:%M:%S',shell=True).replace('\n','')


# if intro == hoy or intro == 'hoy':
#     rango_hora=8    
# elif intro == ayer or intro == 'ayer':
#     hoy=ayer
#     rango_hora=23
#     hora='23:59:59'    
# else:
#     hoy=intro
#     rango_hora=23
#     hora='23:59:59'


#Ignoro todo lo anterior para testear
hoy='0408-2015'
ayer='0308-2015'
rango_hora=8
hora='11:55:00'

#%%
#Define funciones que va a usar para dibujar las lineas
#Una linea tiene un solo color, para poder hacer lineas con distintos colores que dependan una variable extra(La lluvia por ejemplo, o dejar la linea en blanco si no se esta midiendo) se concatenan muchas lineas,
#Esta parte se encarga de concatenar esas lineas con los colores correspondientes, ademas, devuelve algunos valores importantes para el grafico (Esto se copio directo de un ejemplo de internet...nadie sabe como funciona)
def dibujar(x,y,color,check):
    y=suavizar(y,check)    
    cmap=ListedColormap(['white',color])
    norm=BoundaryNorm([0,0,5],cmap.N)
    a=np.asarray(y)    
    points=np.array([x,a]).T.reshape(-1,1,2)
    segments=np.concatenate([points[:-1],points[1:]],axis=1)
    lc=LineCollection(segments,cmap=cmap,norm=norm)
    lc.set_array(np.asarray(check))
    lc.set_linewidth(1.2)
    ymax=max([float(v) for v in y])    
    ymin=min([float(v) for v in y])    
    return lc,ymin,ymax

#Lo mismo que el anterior, pero este con mas colores para los distontos estados de nubes.
def dibujarsky(x,sky,rain):
    sky=suavizar(sky,rain)
    cmap=ListedColormap(['k','white','r','b','y'])
    norm=BoundaryNorm([-1,-0.5,0.1,0.5,1,2],cmap.N)
    a=np.asarray(sky)
    points=np.array([x_cloud,a]).T.reshape(-1,1,2)
    segments=np.concatenate([points[:-1], points[1:]],axis=1)
    lc=LineCollection(segments,cmap=cmap,norm=norm)
    lc.set_array(np.asarray(rain))
    lc.set_linewidth(1.2)
    min1=min([float(v) for v in sky])
    max1=max([float(v) for v in sky])
    return lc,min1,max1

#Cuando las estaciones dejan de medir, en el grafico aparecia una recta a 0 del color de la linea. Esto se encarga de hacerla desaparecer.
def suavizar(y,check):
    puntos= [i for i,x in enumerate(check) if x != y[i-1] and x == 0]
    for v in puntos:
        y[v]=y[v-1]
    return y
#%% Define la funcion que importa los datos, requiere 5 entrada, desde que hora y hasta que hora importa los datos, cual es el dia de hoy y cual el de ayer (Los datos pueden estar acomodados en distintos archivos dependiendo el dia )
    #la ultima entrada define si importa los archivos del dia de ayer o del dia de hoy

def importar(desde,hasta,hoy,ayer,boolean):
    superior=int(hasta.replace(':',''))    
    inferior=int(desde.replace(':',''))
    if boolean is True:
        c=open(path_cloudwatcher,'r')
        d=open(path_datos+'Anemometro/'+hoy,'r')
    else:
        c=open(path_datos+'CloudWatcher/'+ayer,'r')
        d=open(path_datos+'Anemometro/'+ayer,'r')
    datos=c.readlines()
    datos1=d.readlines()
    c.close()
    d.close()
    for line in datos[1:-1]:
        a=line.replace('"','').split(',')
        #Si la linea esta completa (20 columnas) y no es basura (como algun header en el medio) sigue.        
        if a[1] != 'Time'and len(a) == 20: 
             if int(a[1].replace(':','')) >= inferior and int(a[1].replace(':',''))<= superior: #revisa que la hora este entre los limites en que va a importar
                h_cloud.append(a[1])             
                x_cloud.append(hora2num(a[1],boolean)) #Guarda la fecha y ademas, a cada fecha le asigna un numero en una escala lineal definida mas abajo (no es facil plotear en funcion de cosas como '13:08:45')
                if a[3] != 'Unknown': #Cuando se desenchufa algun cable, la estacion sigue midiendo pero devuelve "unknown"
                    amb.append(a[6])  #guarda los datos que interesan
                    sky.append(a[5])
                    amb2.append(a[9])
                    check_cloud.append(1)        
                    if a[3] == 'Dry':       #la variable rain va a valer numeros entre -1 y 2, y dependen de si no hay nubes, hay pocas, muchas o esta lloviendo, se usa para poder cambiar los colores de la linea en funcion de esto
                        if a[2] == 'Clear':
                            rain.append(-1)
                        if a[2] == 'Cloudy':
                            rain.append(2)
                        if a[2] == 'Overcast':
                            rain.append(0.3)
                    elif a[3] == 'Wet' or a[3] == 'Rain':
                        rain.append(0.6)
                elif a[3] == 'Unknown':  #Si devuelve unknown, se separan esos datos, se les da un valor numerico (0) y se sigue
                    
                    sky.append(0)
                    amb.append(0)
                    check_cloud.append(0)
                    rain.append(0)
    
    #Aca repite todo pero con los archivos del anemometro los archivos check_ juegan el mismo papel que antes "rain"
    for line in datos1[1:]:
        a=line.split(',')
        if int(a[1].replace(':','')) >= inferior and int(a[1].replace(':',''))<= superior:
            h_anem.append(a[1])            
            x_anem.append(hora2num(a[1],boolean))            
            if '?' in a[2]:
                viento.append(0)
                check_viento.append(0)                
            else:
                 viento.append(a[2])
                 check_viento.append(1)               
            if '?' in a[4]:
                dew.append(0)                
                check_dew.append(0)
            else:
                dew.append(a[4])
                check_dew.append(1)
            if '?' in a[3]:
                humedad.append(0)
                check_humedad.append(0)
            else:
                humedad.append(a[3])
                check_humedad.append(1)

#Aca se define una escala numerica absoluta para las fechas, basicamente es la cantidad de segundos desde las 00hs. Si los datos son de ayer, devuelve un numero negativo.
#Se usa mas adelante para graficar en funcion de esto 
def hora2num(hora,boleean):
    if boleean is True:
        a=0
    else:
        a=24*60*60
    H,M,S=hora.split(':')
    return int(S)+int(M)*60+int(H)*60*60-a          

#%% Define las variables que va a usar 
h_cloud,sky,amb,amb2,rain=[],[],[],[],[]
viento,dew,h_anem,humedad=[],[],[],[]
check_viento,check_dew,check_humedad,check_cloud=[],[],[],[]
x_cloud,x_anem=[],[]

#Importa los datos de las ultimas rango_hora horas, teniendo en cuenta que si es muy temprano, algunos datos pueden estar en los archivos de ayer.
b=int(hora.split(':')[0])-rango_hora
if b>=0:
    desde=str(b)+hora[-6:]
    importar(desde,hora,hoy,ayer,True)
elif b < 0:
    desde=str(24+b)+hora[-6:]
    importar(desde,'23:59:59',hoy,ayer,False)    
    importar('00:00:00',hora,hoy,ayer,True)  



#%% Define un par de cosas para podes plotear. Basicamente busca cuales son los valores numericos que corresponden a las horas en punto (que se hayan medido)
# Ademas, define las etiquetas que se van a usar en los plots (Tal vez se puede hacer mucho mas...simple)

ultima_hora=h_anem[-1][:-6]+':00:00'
ultimo_tic=hora2num(ultima_hora,True)
tic= [ultimo_tic-i*60*60 for i in range(rango_hora+1) if ultimo_tic-i*60*60 > x_anem[0]]
ultimo_slot=[ i for i,x in enumerate(x_anem) if x == ultimo_tic]
labels=[h_anem[v][:-3] for v in [ultimo_slot[0]-i*12 for i in range(rango_hora+1) if ultimo_slot[0]-i*12 >=0] ]

#Define las lineas para cada uno de los graficos, y ademas agarra los valores minimos y maximos
linea_cielo, sky_min, sky_max=dibujarsky(x_cloud,sky,rain)
linea_ambiente, amb_min, amb_max=dibujar(x_cloud,amb,color_ambiente,check_cloud)
linea_humedad, hum_min, hum_max=dibujar(x_anem,humedad,color_humedad,check_humedad)
linea_dew, dew_min, dew_max=dibujar(x_anem,dew,color_dew,check_dew)
linea_viento, viento_min, viento_max=dibujar(x_anem,viento,color_viento,check_viento)


#%%        Crea los graficos y va ploteando
f, (ax1,ax2,ax3,ax4)=plt.subplots(4,sharex=True,figsize=(11.6,8.3))
plt.xticks(tic,labels)
plt.xlim([x_cloud[0],x_cloud[-1]])
plt.xlabel('Hora')

#primer grafico
ax1.add_collection(linea_cielo)
ax1.set_ylim([sky_min-5,sky_max+5])
ax1.set_xticks(tic)
ax1.hlines(-17,x_cloud[0],x_cloud[-1],color=color_overcast,linestyle='dashed',linewidth=1)
ax1.hlines(-23,x_cloud[0],x_cloud[-1],color=color_nublado,linestyle='dashed',linewidth=1)
ax1.grid(which='both',axis='both',color='grey')
ax1.set_ylabel('Temperatura')

#segundo grafico
ax2.add_collection(linea_ambiente)
ax2.add_collection(linea_dew)
ax2.set_ylim(min(amb_min,dew_min)-5,max(amb_max,dew_max)+5)
ax2.grid(which='both',axis='both',color='grey')
ax2.set_ylabel('Temperatura')

#Tercer grafico
ax3.add_collection(linea_humedad)
ax3.set_ylim([0,hum_max+5])
ax3.grid(which='both',axis='both',color='grey')
ax3.set_ylabel('Humedad relativa')

#cuarto grafico
ax4.add_collection(linea_viento)
ax4.set_ylim(0,viento_max+2)
ax4.grid(which='both',axis='both',color='grey')
ax4.set_ylabel('Viento')
plt.savefig('clima.png',dpi=200,bbox_inches=None)

plt.show()