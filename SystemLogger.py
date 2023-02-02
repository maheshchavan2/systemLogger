
from cmath import log
from operator import concat
import platform
from this import s
from unicodedata import name
import psutil
import pymssql
import pymysql as mysql
import mysql.connector

import datetime
import os
#txt
def log_entry(execName):
    log_entry1 = open("log.txt","a")
    L = concat(str(execName) ,  "\n")
    log_entry1.writelines(L)
    log_entry1.close()

def getService(name): 

    service = None 
    try: 
        service = os.system('service ' + name + ' status') #psutil.win_service_get(name) 
    except Exception as ex:
        log_entry(ex) 
        #print(str(ex))

    return service 


def getdbConnection(dbType, host, dbName, user, password):
    if(dbType == 'mysql'):
        return mysql.connector.connect(
            host= str(host),
            database=str(dbName),
            user=str(user),
            passwd= str(password)
        )
    elif(dbType == 'sql'):
        return pymssql.connect(server = host,
                database = dbName,
                user = user,
                password =password)     
    

def getStorageLevel(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return (format(bytes,'.2f') + unit + suffix)
        bytes /= factor


dbType = 'mysql'
host= 'Host _IP'
database='DBA_NAME'
user='USER_Name'
passwd= 'PASSWORD'
db_connection = getdbConnection(dbType, host,database, user,passwd)
class sysInfoModel: 
    def __init__(self, description, value, process): 
        self.description = description 
        self.value = value
        self.process = process
def system_info():
    try:
    
        # creating list       
        list = [] 
    

        tnow = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        uname = platform.uname()
        print("System: " + uname.system)
        print("Node Name: " + uname.node)
        log_entry("--------------------------------------------------------------------------")
        log_entry(tnow)
        log_entry("--------------------------------------------------------------------------")
        svmem = psutil.virtual_memory()
        
        list.append(sysInfoModel('System'.upper(),uname.system,'application server'.upper()))
        list.append(sysInfoModel('Server Name'.upper(),uname.node,'application server'.upper()))
        list.append(sysInfoModel('total ram'.upper(),getStorageLevel(svmem.total),'application server'.upper()))
        list.append(sysInfoModel('available ram'.upper(),getStorageLevel(svmem.available),'application server'.upper()))
        list.append(sysInfoModel('Used ram'.upper(),getStorageLevel(svmem.used),'application server'.upper()))
        list.append(sysInfoModel('ram usage percentage'.upper(),str(svmem.percent) + '%','application server'.upper()))
        list.append(sysInfoModel('cpu usage'.upper(),str(psutil.cpu_percent(interval=0.5)) + '%','application server'.upper()))
        
        
        

        
        TotalStorage = 0
        UsedStorage = 0
        FreeStorage = 0
        
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
            except PermissionError:
                continue
            TotalStorage += partition_usage.total
            UsedStorage += partition_usage.used
            FreeStorage += partition_usage.free

        totalstorage=str(getStorageLevel(TotalStorage))
        usedstorage=str(getStorageLevel(UsedStorage))
        freeStorage=str(getStorageLevel(FreeStorage))

        list.append(sysInfoModel('total storage'.upper(),totalstorage,'application server'.upper()))
        list.append(sysInfoModel('used storage'.upper(),usedstorage,'application server'.upper()))
        list.append(sysInfoModel('free storage'.upper(),freeStorage,'application server'.upper()))
    
        
        service = getService('Historian') 
        
        try:
            if int(service) <1000: 
                log_entry("service is running"+tnow)
                if(int(service) == 0):
                    list.append(sysInfoModel('Status'.upper(),'Running','historian application'.upper()))
                
                else: 
                    log_entry("service is not running"+tnow)
                    list.append(sysInfoModel('Status'.upper(),'Stopped','historian application'.upper()))
            else: 
                log_entry("service not  found"+tnow)
                raise Exception("not found")
        
        
        
        except Exception as e:
            list.append(sysInfoModel('Status'.upper(),'Not Found','historian application'.upper()))
        rowaffected = 0
        mycursor = db_connection.cursor()
        for obj in list:
            print(obj.description + ' ' + obj.value + ' ' + obj.process)
            sql = ''
            if(dbType == 'mysql'):
                sql ="call SA_UpdateSystemInfo('"+ obj.description +"', '"+ obj.value +"' , '"+ obj.process +"')"
            elif(dbType == 'sql'):
                    sql ="exec SA_UpdateSystemInfo '"+ obj.description +"', '"+ obj.value +"' , '"+ obj.process + "'"
            else:
                break
            mycursor.execute(sql)
            db_connection.commit()
            rowaffected+= mycursor.rowcount
            

        if(rowaffected == len(list)):
            log_entry("data updated successfully "+tnow)
        else:
            #print("data not updated",tnow)
            log_entry("data not updated "+tnow)

    except Exception as e:
        log_entry("--------------------------------------------------------------------------")
        log_entry("Error: " + str(e))
            


system_info()
