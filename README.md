# Custom Oracle metrics using Prometheus Python Client + Grafana

<img width="1909" height="931" alt="image" src="https://github.com/user-attachments/assets/a26e81d2-cacb-4a6f-a370-51a06c991f0b" />


## Architecture

<img width="326" height="341" alt="Oracle_metrics drawio" src="https://github.com/user-attachments/assets/bcfa8ae3-82ed-46ac-b100-fefed35af6a2" />


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
 


Each release provides a .py file. You will setup the oracle_prometheus.py as a Windows service or Linux service. 

The oracle_prometheus.py is run without any parameters, you need settings the connection to Oracle XE like hostname, port and SID.

The configuration file
* is located in the same directory as the exporter executable.
* has the YAML format and is provided with the `--config.file` parameter.
* can be used to enable or disable collectors, set collector-specific parameters, and set global parameters.


```
1. Install Oracle XE on WIndows or Linux.
2. 

pip install prometheus-client
```

This package can be found on [PyPI](https://pypi.python.org/pypi/prometheus_client).

## Documentation

Documentation is available on https://prometheus.github.io/client_python

## Links

* [Releases](https://github.com/prometheus/client_python/releases): The releases page shows the history of the project and acts as a changelog.
* [PyPI](https://pypi.python.org/pypi/prometheus_client)
