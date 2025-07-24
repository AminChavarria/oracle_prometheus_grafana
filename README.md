# Custom Oracle metrics using Prometheus Python Client + Grafana

## Instroduction




## Architecture

<img width="426" height="444" alt="oracle_metrics drawio (1)" src="https://github.com/user-attachments/assets/b5a49225-b120-41eb-ba3a-17fc1098d5b5" />



## Installation

The latest release can be downloaded from the [releases page](https://github.com/prometheus-community/windows_exporter/releases).


Install Oracle XE:

Windows https://docs-oracle-com.translate.goog/?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc&_x_tr_hist=true#GUID-7BF9ACDC-1281-494C-AF96-77A25B1BD67D

Linux https://docs-oracle-com.translate.goog/?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc&_x_tr_hist=true#GUID-728E4F0A-DBD1-43B1-9837-C6A460432733

Create schema "monitor" in Oracle XE.

To connect to the first pluggable database (PDB) use:

```
sqlplus sys/[Password]@//localhost:1521/XEPDB1 as sysdba
create schema monitor identified by "<Password>" profile default ACCOUNT UNLOCK;
grant connect to monitor;
```
Create table "bases" on "monitor" schema.
```
create table monitor.bases (id number,nombre_bd varhcar2(25),link2 varchar2(20), status char(1),monitor_inst char(1));
```

Add connection to database in tnsnames.ora file on ORACLE_HOME

Example:

Path: C:\app\oracle\product\21c\homes\OraDB21Home1\network\admin\tnsnames.ora

```
DB1=
  (DESCRIPTION =
    (ADDRESS_LIST =
      (ADDRESS = (PROTOCOL = TCP)(HOST = hostname)(PORT = 1521))
    )
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = ORCL)
    )
  )
```



Create database link to monitoring database remotly, on Oracle PDB:

Example:
```
sqlplus sys/[Password]@//localhost:1521/XEPDB1 as sysdba

CREATE DATABASE LINK LNK_BD1
 CONNECT TO MONITOR
 IDENTIFIED BY <Password>
 USING 'BD1';
```

Test database link:

```
sqlplus sys/[Password]@//localhost:1521/XEPDB1 as sysdba
select 1 from dual@LNK_BD1;
```
 
You must have previously installed and configured Prometheus.

The `oracle_metrics` will expose all metrics from enabled collectors by default.

Add prometheus.yml:

```
- job_name: "Oracle"
    # metrics_path: "/"
    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.
    #- schema: "http"
    static_configs:
      - targets: ["127.0.0.1:7676"]
```

Each release provides a .py file. You will setup the oracle_prometheus.py as a Windows service or Linux service. 

The oracle_prometheus.py is run without any parameters, you need settings the connection to Oracle XE like hostname, port and SID.

```
connection = oracledb.connect(
            user="monitor",
            password="password",
            dsn="hostname:port/SID"
            )
```




## Documentation

Documentation is available on https://prometheus.github.io/client_python
