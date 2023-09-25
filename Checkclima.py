#!/usr/bin/env python 

# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 11:03:10 2015

@author: Belen y Joel
"""

####################################################################
####								####
####								####
####		ALARMAS CLIMATICAS DEL TELESCOPIO MATE		####
####								####             
####		  Estacion meteorologica CloudWatcher		####
####								####
####								####
####								####
####################################################################


import numpy as np
import os, subprocess
import datetime


path_CloudWatcher='/home/telescopio/CloudWatcher.csv'
path_nubes='/home/telescopio/nubes'
path_Contador='/home/telescopio/bin/weather/verycloudy.csv'
path_aagStatus='/home/telescopio/bin/onoff/aagStatus'
path_anemStatus='/home/telescopio/bin/onoff/anemStatus'
path_seguro='/home/telescopio/bin/seguroAAG'
path_estado='/home/telescopio/Estado'
path_Contador_dew='/home/telescopio/bin/weather/dewpoint.csv'
path_archivos='/home/telescopio/DATOS/DatosClima/Anemometro/'
path_Contador_viento='/home/telescopio/bin/weather/viento.csv'


#Numero de veces que este programa tiene que leer Very Cloudy para que cierre todo. 
repeticiones=4



umbral_AAG=120  #Cantidad de seg maxima que se le permite no medir al AAG suponemos 120
umbral_Anem=360 #Cantidad de seg maxima que se le permite no medir al anemometro suponemos 330
umbral_vientomin=25 #Velocidad de viento minima de cierre despues de algunas repeticiones en km/h suponemos 25
umbral_vientomax=39 #Velocidad de viento critica de cierre en km/h suponemos 39
umbral_dewpoint=4 #Diferentecia entre temperatura y punto rocio para el cierre suponemos 5
lim_clear=-17
lim_cloudy=-23


####################   PROTOCOLO DE CIERRE   #######################

def CERRAR(motivo):
    p=subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE) 
    out, err = p.communicate()
    #Busca los procesos con nombre 'session', si encuentra uno mata todo y manda los alertas.
    for line in out.splitlines():  
        if ' session' in line:  #El espacio adelante es porque hay procesos que se llaman gnome-session... 
            os.system('killall session')           
            os.system('closeSession')            
            os.system('zenity --warning --text="Mal tiempo, cerrando cupula." &')
            os.system('echo `date +%Y-%m-%d\ %H:%M:%S` "-- Aborting session..." >> /home/telescopio/telescopio.log')
            os.system('echo `date +%Y-%m-%d\ %H:%M:%S` "-- Motivo:'+motivo+'..." >> /home/telescopio/telescopio.log')
            os.system('echo `date +%Y-%m-%d\ %H:%M:%S` "-- Invoking closeSession..." >> /home/telescopio/telescopio.log')
            alertar(motivo)            
            break #Sale de la funcion


######################   Enviar Mails    ##########################

def alertar(motivo):
	#
	# Comentado por Pablo para evitar la invasion de mails
	#
    #os.system('sendMail belenareal@gmail.com `date +%Y-%m-%d_%H:%M:%S`'+motivo)
    #os.system('sendMail abuccino@iafe.uba.ar `date +%Y-%m-%d_%H:%M:%S`'+motivo)
    #os.system('sendMail mailkindlejoel@gmail.com `date +%Y-%m-%d_%H:%M:%S`'+motivo)
    n=9 #Esto solo es para que no piense que lo que viene abajo es la definicion de alertar
############################ IMPORTA DATOS AAG###############################

def importarAAG():
    try:
        d = file(path_CloudWatcher, "r").readlines()[-2]
        d=d.replace('","','_').replace('"','')
        d=d.split('_')
        t=float(d[5].replace(',','.'))
        if t <= lim_clear:
            g='Clear'
        elif t <= lim_cloudy:
            g='Very Cloudy'
        else:
            g='Overcast'
        
        
        return d[0],d[1],g,d[3],d[9].replace(',','.'),True
    except:
        return '?','?','?','?','?',False
        

#####################  Checkea si la fecha introducida difiere en la actual en menos del umbral en seg###################################

def checkAAG(dia,hora,umbral,load):
    if load is True:
        try:
            hora=hora.split(':')
            dia=dia.split('-')
            dia=[int(i) for i in dia]
            hora=[int(i) for i in hora]
            fecha_med=datetime.datetime(dia[0],dia[1],dia[2],hora[0],hora[1],hora[2])
            hoy=datetime.datetime.today()
            dif=abs((hoy - fecha_med).total_seconds())
            if dif < umbral:
                return True
            return False
        except:
            return False
            
    else:
        return False

#####################   Importa datos del anemometro ###########################

def importarANEM():
    try:
        b=subprocess.check_output('meteo')  #Agarra la salida de meteo y la acomoda
        b=' '.join(b.split('\n')[-2].split()).split(' ')
        c=b[0]+':'+b[1] #Este es olo para ver que hora dice, luego borrar.
        b[0]=int(float(b[0])-3)	#al dato de hora le resta 3
        if b[0] < 0:
            b[0] = int(24+float(b[0]))
        if len(b[1])==1:		#si es necesario le agrega un 0 a los minutos
            b[1]='0'+b[1]		
        return str(b[0])+':'+b[1]+':00',b[4],str(float(b[6])*3.6),True,c
    except:
        return '?','?','?',False,'?'

######################### Revisa los datos del anemometro #############################

def checkANEM(hora,umbral,load):
    if load is True:
        try:
            c=subprocess.check_output('date +%H:%M:%S',shell=True)
            c=c.split(':')            
            b=hora.split(':')
            bf=float(b[0]+b[1])
            cf=float(c[0]+c[1])
            bs=float(b[0])*60*60+float(b[1])*60   
            cs=float(c[0])*60*60+float(c[1])*60+float(c[2])
            if bf <= cf:
                diff=cs-bs
            if bf > cf:
                diff = cs+24*60*60-bs
            if abs(diff)<umbral:
                return True
            else:
                return False
        except:
            return False
    else:
        return False
######################## Importar Nubes ###########################
def importarNUBES():
    try: 
        c=open(path_nubes,'r')
        b=' '.join(c.readlines()[-1].split()).split(' ')
        c.close()
        return b[0],b[1].split('.')[0],b[7],b[9],True
    except:
        return '?','?','?','?',False

        

####################### Abrir y anotar datos ######################

def anotar(archivo,texto,f):
    c = open(archivo, f)
    c.write(texto+'\n')
    c.close()

###################### Guardad datos anemometro ######################

def guardaranem(hora,datos):
    if hora == '?':
        hora=subprocess.check_output('date +%H:%M:%S',shell=True).replace('\n','')
    hoy=subprocess.check_output('date +%Y-%m-%d',shell=True)
    hoy=hoy.strip('\n')
    anio,mes,dia=hoy.split('-')   
    c=open(path_archivos+dia+mes+'-'+anio,'a+')
    g=c.readlines()
    if len(g) == 0:
        c.write('Dia,Hora,Hora programa,Velocidad viento, Humedad relativa,Punto rocio,Temperatura,Status \n')
        c.write(hoy+','+hora+','+datos+'\n')
    else:
        h=g[-1]
        ultima=h.split(',')[1]
        if ultima!=hora:
            c.write(hoy+','+hora+','+datos+'\n')
    c.close()


#####################################################################
############   Verificar estado de CloudWatcher   #################

Dia,Hora,Nubes,Lluvia,Temperatura,load_aag = importarAAG()
Hora_anem,Humedad,Viento,load_anem,Hora_meteo= importarANEM()
Dewpoint='?'

Anem_status=checkANEM(Hora_anem,umbral_Anem,load_anem)
AAG_status=checkAAG(Dia,Hora,umbral_AAG,load_aag)
Anemometro=True
if Anem_status is False:
    Anemometro=False
    anotar(path_anemStatus,'0','w')
    Dia_anem,Hora_anem,Viento,Dewpoint,load_anem=importarNUBES()
    Anem_status=checkAAG(Dia_anem,Hora_anem,umbral_Anem,load_anem)
else:
    anotar(path_anemStatus,'1','w')
    

##################      CloudWatcher      ##################################

if AAG_status is True and Lluvia != 'Unknown': #Cuando se desconecta el cable la estacion sigue guardando datos pero todos unknown. Con esto se fija que este prendida y ademas este midiendo bien.
    anotar(path_aagStatus,'1','w') #Si la estacion esta midiendo pasa a ver la lluvia
    if Lluvia != 'Dry':
        alertar('--Mal-clima,-lluvia')        
        CERRAR('--Mal-clima,-cerrando-por-lluvia')
        anotar(path_seguro,'No es seguro','w') #Si marca cualquier cosa que no sea Dry cierra, si no mira las nubes
    
    elif Nubes == 'Overcast':
        dim=np.loadtxt(path_Contador,delimiter=',')    
        dim=np.size(dim)    
        if dim >= repeticiones+1:
            alertar('--Mal-clima,-nubes')            
            CERRAR('--Mal-clima,-cerrando-por-nubes')
            anotar(path_seguro,'No es seguro','w')            
            anotar(path_Contador,'3','a') #Si la cantidad de veces que ya midio muchas nuves es mayor que tanto, cierra
        
        else: #si no lo es, agrega datos
            anotar(path_seguro,'Es seguro','w')            
            anotar(path_Contador,'3','a')            
                     
    else: #es ecir, mide, no hay lluvia ni nubes.
        anotar(path_seguro,'Es seguro','w')            
        anotar(path_Contador,'2','w')
else: #aca va lo que hace si la estacion no esta midiendo o por algun motivo, check no devuelve True
    anotar(path_seguro,'No es seguro','w')
    anotar(path_aagStatus,'0','w')
    os.system('echo `date +%Y-%m-%d\ %H:%M:%S` "-- CloudWatcher NO esta midiendo..." >> /home/telescopio/telescopio.log')
    alertar('--La-estacion-AAG-NO-esta-midiendo')    
    CERRAR('--La-estacion-AAG-NO-esta-midiendo')




######################      Estacion de respaldo     ########################


#Similar para el anemometro, usa el dia del cloudwatcher porque no tenemos nada...
if Anem_status is True:
    anotar(path_anemStatus,'1','w')

    if float(Viento) > umbral_vientomax: #Viento mayor al valor maximo
        CERRAR('--Mal-clima,-cerrando-por-viento')
        anotar(path_seguro,'No es seguro','w')
        alertar('--Mal-clima,-viento')

    elif float(Viento) > umbral_vientomin: #Viento entre el valor minimo y maximo
        dim=np.loadtxt(path_Contador_viento,delimiter=',')
        dim=np.size(dim)
        if dim >= repeticiones+2:           
            CERRAR('--Mal-clima,-por-viento')
            anotar(path_seguro,'No es seguro','w')
            alertar('--Mal-clima,--por-viento') #para testear
            anotar(path_Contador_viento,'1','a')
            anotar(path_seguro,'No es seguro','w')
        else:
             anotar(path_Contador_viento,'3','a')
             anotar(path_seguro,'Es seguro','w')
    else:
        anotar(path_Contador_viento,'2','w')
        anotar(path_seguro,'Es seguro','w')   
    
    
    if Dewpoint is '?' and AAG_status is True: # mide el punto de rocio
        Dewpoint=(float(Humedad)/100.0)**(1/8.0)*(110-float(Temperatura))-110
    
    if float(Temperatura) - float(Dewpoint) < umbral_dewpoint:
        dim=np.loadtxt(path_Contador_dew,delimiter=',')    
        dim=np.size(dim)              
        if dim >= repeticiones+1:           
            CERRAR('--Mal-clima,-temperatura-cercana-a-punto-de-rocio')
            anotar(path_seguro,'No es seguro','w')
            alertar('--Mal-clima,-temperatura-cercana-a-punto-de-rocio') #para testear
            anotar(path_Contador_dew,'1','a')
            anotar(path_seguro,'No es seguro','w')
        else:
            anotar(path_Contador_dew,'3','a')
            anotar(path_seguro,'Es seguro','w')
    else:
        anotar(path_Contador_dew,'2','w')
        anotar(path_seguro,'Es seguro','w')   
else:
    anotar(path_anemStatus,'0','w')
    anotar(path_seguro,'No es seguro','w')
    os.system('echo `date +%Y-%m-%d\ %H:%M:%S` "--No-se-puede-acceder-a-datos-de-anemometro..." >> /home/telescopio/telescopio.log')
    alertar('--No-se-puede-acceder-a-datos-de-anemometro')    
    CERRAR('--No-se-puede-acceder-a-datos-de-anemometro')

guardaranem(Hora_anem,Hora_meteo+','+Viento+','+Humedad+','+str(Dewpoint)+','+Temperatura+','+str(Anemometro))
anotar(path_estado,' Dia = '+Dia+'\n horaAAG = '+Hora+'\n horaAnemom = '+Hora_anem+'\n Lluvia = '+Lluvia+'\n Nubes = '+Nubes+'\n Viento = '+Viento+'\n Humedad = '+Humedad+'\n Punto rocio  = '+str(Dewpoint)+'\n Temperatura  = '+Temperatura,'w')

    
##################################################################