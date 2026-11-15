from machine import I2C, Pin
import utime
import time

opcion=0
min_ac=-1
min_cambio=0
min_cont=-1
ok_cont=0
bandera=0

#print('hola')
alarma_info = open('alarma.txt', 'r')
datos = alarma_info.read()
alarma_info.close()
min_al, horas_al = datos.split(',')
min_al = int(min_al)
horas_al = int(horas_al)
#print(horas_al,min_al)
disp=4
letrero=-1
alicia=0

inicio=0
set_op=Pin(19,Pin.IN)
buzzer=Pin(22,Pin.OUT)
up_op=Pin(16,Pin.IN)
ok_op=Pin(17,Pin.IN)
matriz_num=[[1,1,1,1,1,1,0],
            [0,1,1,0,0,0,0],
            [1,1,0,1,1,0,1],
            [1,1,1,1,0,0,1],
            [0,1,1,0,0,1,1],
            [1,0,1,1,0,1,1],
            [1,0,1,1,1,1,1],
            [1,1,1,0,0,0,0],
            [1,1,1,1,1,1,1],
            [1,1,1,0,0,1,1]]

instruccion=[[1,1,1,0,1,1,1], #A0
             [0,0,0,1,1,1,0], #L1
             [1,0,0,1,1,1,0], #C2
             [0,0,0,0,0,0,1],  #-
             [0,1,1,1,1,0,1], #d4
             [0,0,1,0,1,0,1], #n5
             [1,1,0,1,1,1,1],  #e6
             [1,0,1,1,0,1,1],# S7
             [0,0,0,0,0,0,0], #none8
             [1,1,0,0,1,1,1], # P9
             [2,1,2,0,0,0,0],  #clc
             [1,1,1,1,1,1,0],   #o11
             [0,0,0,0,1,0,1],  #r12
             [1,1,1,1,0,1,1],   #g13
             
    ]

alfa=[[8,0,1,0],  #ala
      [8,2,1,2],  #clc
      [6,5,11,4],  #done
      [7,7,0,9],   #pass
      [8,12,1,2],   #clr
      [3,11,13,3],  #-go-
      [8,8,8,8],  #
    ]

'''PINES GPIO'''
pines=[]

for i in range(7):
    pines.append(Pin(i, Pin.OUT))
'''CONEXION I2C'''

ds_i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=400000)

def get_bcd(bcd):
    unidad=bcd[0]&15
    decena=(bcd[0]>>4)
    numero=unidad+decena*10
    return numero

def back_bcd(set_time):
    num=((set_time//10)<<4)| set_time%10
    return bytes([num])

ultimo_press=0
filtro=100
ahora=0

def cambio(pin):
    global opcion,ultimo_press
    #print('verde')
    if opcion<3:
        opcion+=1.     
    else:
        opcion=0
        
        
def ban_up(pin):
    global bandera,opcion,min_cont
    #print('rojo')
    if opcion > 0:
        bandera=1
        min_cont+=1
        
def ok_set(pin):
    global ok_cont, alicia
    #print('negro')
    if bandera > 0 and opcion > 0: ###########cambio
        ok_cont+=1

        
        
def puerto(actual):
    for i in range(10):
        if actual==i:
            for j in range(7):
                pines[j].value(matriz_num[actual][j])
            break
            
     
def display(hora,minu):
        hora_tot[0]=minu%10
        hora_tot[1]=minu//10
        hora_tot[2]=hora%10
        hora_tot[3]=hora//10
        #print(f'minuto uni{hora_tot[0]}, minuto dec{hora_tot[1]},hora uni{hora_tot[2]},hora dec{hora_tot[3]}')
        for i in range(len(digitos)):
            puerto(hora_tot[i])
            digitos[i].on()
            time.sleep(0.001)
            digitos[i].off()
            
def display_alfa(letrero):
    for i in range(len(digitos)):
        for j in range (7):
            pines[j].value(instruccion[alfa[letrero][i]][j])
        digitos[i].on()
        time.sleep(0.001)
        digitos[i].off()


def puerto(actual):
    for i in range(10):
        if actual==i:
            for j in range(7):
                pines[j].value(matriz_num[actual][j])
            break
        
hora_tot=[0,0,0,0]


digitos=[
    Pin(10,Pin.OUT),
    Pin(9,Pin.OUT),
    Pin(8,Pin.OUT),
    Pin(7,Pin.OUT)
    ]

t = time.localtime()
hora = t[3]
minuto = t[4]
segundo = t[5]
ds_i2c.writeto_mem(0x68, 0x00, back_bcd(segundo))  
ds_i2c.writeto_mem(0x68, 0x01, back_bcd(minuto))
ds_i2c.writeto_mem(0x68, 0x02, back_bcd(hora))


set_op.irq(trigger=Pin.IRQ_FALLING, handler=cambio)
up_op.irq(trigger=Pin.IRQ_FALLING, handler=ban_up)
ok_op.irq(trigger=Pin.IRQ_FALLING, handler=ok_set)

        
def read_time():
    min = ds_i2c.readfrom_mem(0x68, 0x01, 2) ##min
    horas = ds_i2c.readfrom_mem(0x68, 0x02, 2) ##horas
    return get_bcd(min),get_bcd(horas)


def config_minho(m,h):
    global min_cont, ok_cont, opcion, bandera
    min_cambio=0
    hor_cambio=0

    if opcion ==1:
        letrero=0
        display_alfa(letrero)
    if opcion == 2:
        letrero=1
        display_alfa(letrero)  
    while bandera>0 and opcion > 0: #usuario quiere setear un tiempo
        miho_cont=0  
        if min_cont>-1 and ok_cont==0: #cambio de minutos
            min_cambio=m+min_cont
            pedro=ok_cont
            if min_cambio<60:
                display(h,min_cambio)
            else:
                letrero=4
                min_cont=0
                min_cambio=0
                m=0
                inicio = time.ticks_ms()
                while time.ticks_diff(time.ticks_ms(), inicio) < 1000:
                    display_alfa(letrero) 

                
            if pedro != ok_cont:
                letrero=3
                min_cont=0
                inicio = time.ticks_ms()
                while time.ticks_diff(time.ticks_ms(), inicio) < 1000:
                    display_alfa(letrero) 
    
        if min_cont>-1 and ok_cont==1:     #cambio de horas
            hor_cambio=h+min_cont
            if hor_cambio<24:
                display(hor_cambio,min_cambio)
            else:
                letrero=3
                min_cont=0
                hor_cambio=0
                h=0
                inicio = time.ticks_ms()
                while time.ticks_diff(time.ticks_ms(), inicio) < 1000:
                    display_alfa(letrero)

        if ok_cont==2:
            bandera=0
            opcion=0
            break
    return min_cambio,hor_cambio
 

while True:
    m,h = read_time()
    if opcion == 0:
        display(h,m)
    if opcion == 1:
        min_al_se,horas_al_se=config_minho(m,h)
        if ok_cont == 2:
            letrero=2
            inicio = time.ticks_ms()
            alarma_info=open('alarma.txt','w')
            alarma_info.write(str(min_al_se) + ',' + str(horas_al_se))
            alarma_info.close()
            while time.ticks_diff(time.ticks_ms(), inicio) < 2000:
                display_alfa(letrero)   
            ok_cont=0
            alicia=0
            
    if opcion == 2:
        minutos,horas=config_minho(m,h)
        if ok_cont == 2:
            letrero=2
            inicio = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), inicio) < 2000:
                display_alfa(letrero) 
            ds_i2c.writeto_mem(0x68, 0x01, back_bcd(minutos))
            ds_i2c.writeto_mem(0x68, 0x02, back_bcd(horas))
            ok_cont=0
    if opcion == 3:
        letrero=0
        inicio = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), inicio) < 1000:
                display_alfa(letrero)
        inicio = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), inicio) < 1000:
                display(horas_al,min_al)
        opcion=0
      
        
    if m==min_al and h==horas_al and alicia==0:
            inicio = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), inicio) < 500:
                display(horas_al,min_al)
                buzzer.on()
                if ok_op.value()==0:
                    alicia=1
                    break
            letrero=6
            inicio = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), inicio) < 500:
                display_alfa(letrero)
                buzzer.off()
                if ok_op.value()==0:
                    alicia=1
                    break
    if m != min_al:
        alicia=0
        
        
        




            
        
        
        
        
        

      
        
    

    
        
    