import oracledb
import time
import datetime
import random
from prometheus_client import start_http_server, Counter, Info, Gauge, Enum
import prometheus_client

#deshabilita las metricas por default de python
prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

# NO SE PUEDE UTILIZAR Enum porque no acepta labels para identificar cada base de datos
#e_instance_status = Enum('ora_instance_status', 'Status instance',['base'],states=['OPEN', 'STOPPED'])

#Prod env

g_sa  = Gauge('ora_session_status_total', 'Sesiones status por BD',['base', 'status'])
g_sau = Gauge('ora_session_active_by_user', 'Sesiones activas por usuario',['base', 'username'])
g_siu = Gauge('ora_session_inactive_by_user', 'Sesiones inactivas por usuario',['base', 'username'])
g_st  = Gauge('ora_session_by_user_total', 'Sesiones totales por usuario',['base', 'username']) 
g_slt = Gauge('ora_session_locks_total', 'Sesiones bloqueos total',['base'])
g_instance_status = Gauge('ora_instance_status', 'Status instance',['base','status'])

#clase             
class CollectorOracle:
    
    #constructor
    def __init__(self, ):
        #i = Info("ora_db_info", "Estado de la instancia")
        a=1
        
    #metodo set 
    def collect_info(self, ):
        #self.metric_enum.state('OPEN')

        try:
            connection = oracledb.connect(
            user="user",
            password="password",
            dsn="hostname:port/SID"
            )
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        else:
            cursor = connection.cursor()
        finally:            
            print("Successfully connected to Oracle Database")
            
        #try:
            
            # DB Links
            cursor.execute("SELECT LINK2, nombre_bd FROM monitor.bases WHERE status = 1 AND monitor_inst = 1 order by 1")
            rows_db_catalog = cursor.fetchall()
            for dbc in rows_db_catalog:
    
                print("link = " + dbc[0])
       
                try:
                    print("Obteniendo metricas")
                    cursor_db = connection.cursor()
                    cursor_db.execute("SELECT instance_name, status, startup_time FROM v$instance@" + dbc[0])
                    error_ora = False   
                       
                except Exception as e: 
                    # Log error as appropriate
                    error, = e.args
                    print('TENEMOS UN ERROR ---->')
                    print('Error.code =', error.code)
                    print('Error.message =', error.message)
            
                    # ORA-12541: TNS:no listener
                    # ORA-12545: Connect failed because target host or object does not exist
                    # ORA-12154: TNS:could not resolve the connect identifier specified, 
                    # ORA-12514: TNS:listener does not currently know of service requested in connect descriptor
                    # ORA-12170: TNS:Connect timeout occurred
                    if (error.code > 12100):                               
                        error_ora = True
                
                else:
                    rows_db_status = cursor_db.fetchall()
                    
                #Validamos si se presenta un ORA- en la conexion y entonces set estados STOPPED
                if error_ora is True:
                    g_instance_status.labels(base=str(dbc[1]),status='OPEN').set(0)   # 0 = down                                    
                    print('Error ORA status =' + str(error_ora))                
                else:
                    for inst_det in rows_db_status:
                        if inst_det[1] == 'OPEN':
                            g_instance_status.labels(base=str(dbc[1]),status='OPEN').set(1)
                    
                   
                
                    #sesiones ACTIVE por BD siempre y cuando error_ora IS FALSE
                    cursor_db.execute("SELECT status, count(*) FROM v$session@"+ dbc[0] + " WHERE status = 'ACTIVE' and username !='SYS' group by status")
                    rows_db_ses_act = cursor_db.fetchall()
                
                    for ses_active in rows_db_ses_act:
                        g_sa.labels(base=str(inst_det[0]), status=str(ses_active[0])).set(ses_active[1])
                
                
                    #sesiones TOTAL ACTIVE por usuario
                    cursor_db.execute("SELECT username, count(*) FROM v$session@"+ dbc[0] + " WHERE status='ACTIVE' and username !='SYS' group by username")
                    rows_db_ses_act_by_user = cursor_db.fetchall()
                        
                    for ses_active_by_user in rows_db_ses_act_by_user:
                        g_sau.labels(base=str(inst_det[0]), username=str(ses_active_by_user[0])).set(ses_active_by_user[1])
                
                    #sesiones TOTAL INACTIVE por usuario
                    cursor_db.execute("SELECT username, count(*) FROM v$session@"+ dbc[0] + " WHERE status='INACTIVE' and username !='SYS' group by username")
                    rows_db_ses_ina_by_user = cursor_db.fetchall()
                        
                    for ses_inactive_by_user in rows_db_ses_ina_by_user:
                        g_siu.labels(base=str(inst_det[0]), username=str(ses_inactive_by_user[0])).set(ses_inactive_by_user[1])
                        
                    #sesiones TOTAL
                    cursor_db.execute("SELECT username, count(*) FROM v$session@" + dbc[0] + " WHERE username !='SYS' group by username order by 2 desc")
                    rows_db_ses_total = cursor_db.fetchall()
                        
                    for ses_total in rows_db_ses_total:
                        g_st.labels(base=str(inst_det[0]), username=str(ses_total[0])).set(ses_total[1])
                
                    #1 minuto bloqueos exclusivos
                    '''
                    2 - ROWS_S (SS): Row Share Lock
                    3 - ROW_X (SX): Row Exclusive Table Lock
                    4 - SHARE (S): Share Table Lock
                    5 - S/ROW-X (SSX): Share Row Exclusive Table Lock
                    6 - Exclusive (X): Exclusive Table Lock
                    '''     
                    cursor_db.execute("SELECT count(*) FROM v$locked_object@"+ dbc[0] + " a,v$session@"+ dbc[0] + " b,dba_objects@"+ dbc[0] + " c WHERE b.sid = a.session_id AND c.object_name not like 'AQ_%' and b.program not like 'ORACLE.EXE (SHAD)%' and (b.program not like '%CKPT%' or b.program not like '%J0%' or b.program not like '%ARC%' ) AND a.object_id = c.object_id AND a.locked_mode in (3,5,6) AND b.last_call_et > 60")
                    rows_db_ses_lock_total = cursor_db.fetchall()
       
                    for ses_locks_total in rows_db_ses_lock_total:
                        if ses_locks_total[0] is None:
                            g_slt.labels(base=str(inst_det[0]) ,owner=str(ses_locks_total[0])).set(0)
                        else:
                            g_slt.labels(base=str(inst_det[0])).set(int(ses_locks_total[0]))
                               

def process_request():
    x = datetime.datetime.now()
    print ("Conectando..." + str(x))
  
#main     
if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(7676)
    
    collector = CollectorOracle()
    
    while True:
        time.sleep(10)
        collector.collect_info()                                 
        