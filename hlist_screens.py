import logging

# Create a logger for the screenDefs module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(funcName)s:%(message)s')

file_handler = logging.FileHandler('dbUtil.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Comment out the next 3 lines if you don't want log 
# messages displaying on the console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)



main_window = None
debug = False
displayed_query = None
editor = 'notepad.exe'
SQLPlus = 'sqlplus.exe'
gNOTEPAD=0
#-------------------------------------------------------------
#  Define the available databases that can be selected from the
#  database dropdown list.
#-------------------------------------------------------------

gDBs=[ {'db':'------- LOCAL -------'},
       {'db':'PYDB',
       'SID':'PYDB',
       'port':1523,
       'host':'127.0.0.1'}
       
     ]
def getDBs():
   """
     Return the list of databases that the program can
     connect to
   """
   return gDBs



def get_screen_def(screen_name):
   """
      Returns the screen definition dictionary object
     for the desired screen
   """
   for i, screen in enumerate(screens):
      if debug:
         logger.debug('Screen #{} = {}'.format(i,screen['name']))
      if screen['name'].find(screen_name) == 0:
         return(screens[i])



"""
               Tix Scrolled HLists Screen Definitions 
    screens is a list of dictionary objects defining the various  
   screens i.e. Tix Scrolled HLists that are displayed. The 'query' 
   keyword of the screen's dictionary object defines the SQL query
   that populates the HList.
"""


screens=[ 
{ 'name' : 'UserList',
  'hlist' : 'hlstUsers',
  'window' : 'winUsers',
  'title' : 'Database Users',
  'columns' : [('username', 'Oracle User'), ('account_status', 'Account Status'),
               ('default_tablespace', 'Default Tablespace'),
               ('temporary_tablespace', 'Temporary Tablespace'),
               ('profile', 'Profile'), ('ptime', 'Password Last Changed'),
               ('expiry_date', 'Password Expires'),('lock_time', 'Password Last Locked'),
               ('initial_rsrc_consumer_group', 'Initial Consumer Group')], 
  'query' : """ SELECT u.username,
			u.account_status,
			default_tablespace,
			temporary_tablespace,
			profile,
			su.ptime,
			u.expiry_date,
			TO_CHAR(su.ltime,'MON DD YYYY hh:miAM') lock_time,
			initial_rsrc_consumer_group
		 FROM dba_users u,
		      sys.user$ su
		 WHERE u.username = su.name
		 ORDER BY var_order_by
		""",
  'order_by' : 'username',
  'sortOrder' : 'ASC',
  'selectionSource' : None,
  'selectMode' : 'extended',
  'command' : 'getUserObjects',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'dbUsers.txt',
  'outputColumns' : [0,1,2,3,4,5,6]
},
{ 'name' : 'UserJobs',
  'hlist' : 'hlstUserJobs',
  'window' : 'winUserJobs',
  'title' : 'User Jobs',
  'columns' : [('username', 'User Name'), ('job_name', 'Job Name'),
               ('job_desc', 'Job Description')],
  'query' : 'Dynamically constructed in the sub getUserJobs',
  'order_by' : 'job_name',
  'sortOrder' : 'ASC',
  'selectionSource' : 'UserJobs',
  'selectMode' : 'extended',
  'command' : 'getUserJobs',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'user_jobs.txt',
  'outputColumns' :  [0,1,2]
},
{ 'name' : 'UserRoles',
  'hlist' : 'hlstUserRoles',
  'window' : 'winUserRoles',
  'title' : 'User Roles',
  'columns' : [('grantee', 'Grantee'), ('granted_role', 'Granted Role'),
               ('admin_option', 'Admin Option'), ('default_role', 'Default Role')],
  'query' : 'Dynamically constructed in the sub getUserRoles',
  'order_by' : 'grantee,granted_role',
  'sortOrder' : 'ASC',
  'selectionSource' : 'UserRoles',
  'selectMode' : 'extended',
  'command' : 'getUserRoles',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'user_roles.txt',
  'outputColumns' :  [0,1,2,3]
},
{ 'name': 'DBMSOutput',
  'hlist': 'hlstDBMS_OUTPUT',
  'window': 'winDBMS_OUTPUT',
  'title': 'DBMS_OUTPUT',
  'columns':[('DBMS_OUTPUT', 'DBMS_OUTPUT')],
  'query':'Constructed by the sub displayDBMS_OUTPUT',
  'order_by': None,
  'sortOrder': 'ASC',
  'selectionSource':'DBMSOutput',
  'selectMode': 'extended',
  'command': 'sendToEditor',
  'outputProgram': gNOTEPAD,
  'outputFile': 'JobDBMS_OUTPUT.txt',
  'outputColumns': [0]
},
{ 'name' : 'DBA_Objects',
  'hlist' : 'hlstDBA_Objects',
  'window' : 'winDBA_Objects',
  'title' : 'DBA Objects ',
  'columns' : [('owner', 'OWNER'), ('object_name', 'Object Name'),
               ('object_type', 'Object Type'), ('status', 'Status'),
               ('created', 'Created'), ('last_ddl_time', 'Last DDL Time'),
               ('timestamp', 'Timestamp')],
  'query' :'Constructed by the sub findDBObject',
  'order_by' : 'owner,object_name,object_type',
  'sortOrder' : 'ASC',
  'selectionSource' :'DBA_Objects',
  'selectMode' : 'extended',
  'command' : 'sendToEditor',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'DBAObject.txt',
  'outputColumns' : [0,1,2,3,4,5,6]
},
{ 'name' : 'ObjectAcessPrivs',
  'hlist' : 'hlstObjectAccessPrivs',
  'window' : 'winObjectAccessPrivs',
  'title' : 'Object Access Privs ',
  'columns' : [('owner', 'Owner'), ('table_name', 'Object Name'),
               ('grantee', 'Grantee'), ('privilege', 'Privilege'),
               ('grantor', 'Grantor')],
  'query' :'Constructed by the sub displayObjectAccessPrivs',
  'order_by' : 'owner,table_name,grantee,privilege',
  'sortOrder' : 'ASC',
  'selectionSource' :'DBA_Objects',
  'selectMode' : 'extended',
  'command' : 'sendToEditor',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'ObjectAccessPrivs.txt',
  'outputColumns' : [0,1,2,3,4]
},
{ 'name': 'DBA_Roles',
  'hlist': 'hlstDBA_ROLES',
  'window': 'winDBA_ROLES',
  'title': 'Roles ',
  'columns':[('role', 'Role')],
  'query':"""SELECT role 
             FROM dba_roles 
	     ORDER BY var_order_by
       """,
  'order_by': 'role',
  'sortOrder': 'ASC',
  'selectionSource':'DBA_Roles',
  'selectMode': 'extended',
  'command': 'sendToEditor',
  'outputProgram': gNOTEPAD,
  'outputFile': 'DBA_Roles.txt',
  'outputColumns': [0]
},
{ 'name' : 'ObjectAccessByRoles',
  'hlist' : 'hlstObjectAccessByRoles',
  'window' : 'winObjectAccessByRoles',
  'title' : 'Object Access Privs ',
  'columns' : [('owner', 'Owner'), ('table_name', 'Object Name'),
               ('grantee', 'Grantee'), ('appl_name', 'APPL Name'),
               ('privilege', 'Privilege')],
  'query' :'Constructed by the sub displayObjectAccessPrivs',
  'order_by' : 'owner,table_name,grantee,appl_name,privilege',
  'sortOrder' : 'ASC',
  'selectionSource' :'DBA_Objects',
  'selectMode' : 'extended',
  'command' : 'sendToEditor',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'ObjectAccessPrivs.txt',
  'outputColumns' : [0,1,2,3,4] 
},
{ 'name': 'AllRefConstraintss',
  'hlist': 'hlstAllRefConstraintss',
  'window': 'winAllRefConstraints',
  'title': 'All Referential Constraints ',
  'columns':  [('owner', 'Owner'), ('table_name', 'Table'),
               ('constraint_name', 'Constraint'), ('status', 'Status'),
               ('ref_constraint', 'Ref Constraint'), ('ref_owner', 'Ref Owner'),
               ('ref_table', 'Ref Table'), ('ref_column', 'Ref Column')],
  'query':'Constructed by the sub displayRefConstraints',
  'order_by': 'owner,table_name',
  'sortOrder': 'ASC',
  'selectionSource':'AllRefConstraintss',
  'selectMode': 'extended',
  'command': 'sendToEditor',
  'outputProgram': gNOTEPAD,
  'outputFile': 'Resources.txt',
  'outputColumns': [0,1,2,3,4,5,6,7]
},
{ 'name': 'AllUsersConstraints',
  'hlist': 'hlstAllUsersConstraints',
  'window': 'winAllUsersConstraints',
  'title': 'All Users Constraints ',
  'columns': [('owner', 'Owner'), ('table_name', 'Table'),
              ('constraint_name', 'Constraint'), ('column_name', 'Column'),
              ('search_condition', 'Search Condition'),
              ('constraint_type', 'Constraint Type'), ('status', 'Status'),
              ('ref_constraint', 'Ref Constraint'), ('ref_owner', 'Ref Owner'),
              ('ref_table', 'Ref Table'), ('ref_column', 'Ref Column')],
  'query':'Constructed by the sub displayAllUsersConstraints',
  'order_by': 'owner,table_name',
  'sortOrder': 'ASC',
  'selectionSource':'AllUsersConstraints',
  'selectMode': 'extended',
  'command': 'sendToEditor',
  'outputProgram': gNOTEPAD,
  'outputFile': 'Resources.txt',
  'outputColumns': [0,1,2,3,4,5,6,7]
},
{ 'name' : 'Sessions',
  'hlist' : 'hlstSessions',
  'window' : 'winSessions',
  'title' : 'User Sessions ',
  'columns' :[('osuser', 'OSUser'),
              ('username', 'Username'),
              ('sid', 'SID'),
              ('serial#', 'Serial #'),
              ('os_pid', 'OS PID'),
              ('aud_sid', 'Audit SID'),
              ('machine', 'Machine'),
              ('terminal', 'Terminal'),
              ('status', 'Status'),
              ('command', 'Command'),
              ('logon_time', 'Logon Time'),
              ('program', 'Program'),
              ('duration_min', 'Duration (Mins)'),
              ('latchwait', 'Latch Wait'),
              ('latchspin', 'Latch Spin'),
              ('pga_used_mem', 'PGA Memory Used (KB)'),
              ('pga_alloc_mem', 'PGA Memory Allocated (KB)'),
              ('pga_max_mem', 'PGA Memory Maximum (KB)'),
              ('pga_freeable_mem', 'PGA Memory Freeable (KB)')], 
  'query' :"""SELECT s.osuser osuser,
                       s.username username,
                       s.sid sid,
                       s.serial# serial#,
                       p.spid os_pid,
                       s.audsid aud_sid,
                       s.machine machine,
                       s.terminal terminal,
                       s.status status,
                       DECODE(s.command,
                        0,'No command',
                        1,'Create table' ,
                        2,'Insert',
                        3,'Select' ,
                        6,'Update',
                        7,'Delete' ,
                        9,'Create index',
                        10,'Drop index' ,
                        11,'Alter index',
                        12,'Drop table' ,
                        13,'Create seq',
                        14,'Alter sequence' ,
                        15,'Alter table',
                        16,'Drop sequ.' ,
                        17,'Grant',
                        19,'Create synonym' ,
                        20,'Drop synonym',
                        21,'Create view' ,
                        22,'Drop view',
                        23,'Validate index' ,
                        24,'Create procedure',
                        25,'Alter procedure' ,
                        26,'Lock table',
                        42,'Alter session' ,
                        44,'Commit',
                        45,'Rollback' ,
                        46,'Savepoint',
                        47,'PL/SQL Exec' ,
                        48,'Set Transaction',
                        60,'Alter trigger' ,
                        62,'Analyze Table',
                        63,'Analyze index' ,
                        71,'Create Snapshot Log',
                        72,'Alter Snapshot Log' ,
                        73,'Drop Snapshot Log',
                        74,'Create Snapshot' ,
                        75,'Alter Snapshot',
                        76,'drop Snapshot' ,
                        85,'Truncate table',
                         '? : '||s.command) command,
                       TO_CHAR(s.logon_time,' Mon-DD-YYYY HH24:MI ') logon_time,
                       s.program  program,
                       ROUND((s.last_call_et/60),2) duration_min,
                                       latchwait,
                                       latchspin,
                                       ROUND(pga_used_mem / 1024 ) pga_used_mem,
                                       ROUND(pga_alloc_mem / 1024) pga_alloc_mem,
                                       ROUND(pga_max_mem / 1024) pga_max_mem,
                                       ROUND(pga_freeable_mem / 1024) pga_freeable_mem
                  FROM v$session s,
                       v$process p,
                       v$transaction t,
                       v$rollstat r,
                       v$rollname n
                  WHERE s.paddr = p.addr
                    AND s.taddr = t.addr (+)
                    AND t.xidusn = r.usn (+)
                    AND r.usn = n.usn (+) 
                  ORDER BY var_order_by
                  """,
  'order_by' : 'osuser',
  'sortOrder' : 'ASC',
  'selectionSource' : None,
  'selectMode' : 'extended',
  'command' : 'sendToEditor',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'sessions.txt',
  'outputColumns' : [0,1,2,3,4,5,6,7,8,9]
},
{ 'name' : 'DBA_Tablespaces',
  'hlist' : 'hlistDbaTablespaces',
  'window' : 'winDbaTablespaces',
  'title' : 'DBA Tablespaces',
  'columns' : [('tablespace_name', 'Tablespace Name'),('block_size', 'Block Size'),
               ('initial_extent', 'Initial Extent'),('next_extent', 'Next Extent'),
               ('min_extents', 'Min Extents'),('max_extents', 'Maximum Extents'),
               ('pct_increase', '% Increase'),('contents', 'Contents'),
               ('extent_management', 'Extent Management'),
               ('segment_space_management', 'Segment Space Management')],
  'query' : """ SELECT tablespace_name,
                       block_size,
                       initial_extent,
                       next_extent,
                       min_extents,
                       max_extents,
                       pct_increase,
                       contents,
                       extent_management,
                       segment_space_management
                 FROM dba_tablespaces
      ORDER BY var_order_by
          """ ,
  'order_by' : 'tablespace_name',
  'sortOrder' : 'ASC',
  'selectionSource' : 'DBA_Tablespaces',
  'selectMode' : 'single',
  'command' : 'getTablespaceDataFiles',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'tablespaces.txt',
  'outputColumns' : [0,1,2,3,4,5,6,7,8,9]
},
{ 'name' : 'FreeSpace',
'hlist' : 'hlstFreeSpace',
'window' : 'winFreeSpace',
'title' : 'Tablespace Free Space',
'columns' : [('tablespace_name', 'Tablespace Name'), ('tblspc_size', 'Size (MB)'),
             ('mbytes_free', 'Free Space (MB)'),('percent_used', '% Space Used'),
             ('largest_chunk', 'Largest Free Chunk (MB)'),
             ('max_extents', 'Maximum Extents'),
             ('extent_management', 'Extent Management'),
             ('object_count', 'Objects in Tablespace')],
'query' : """ SELECT fs.tablespace_name,
                     df.tblspc_size,
                     fs.mbytes_free,
                     ROUND((1-fs.mbytes_free/df.tblspc_size)*100,2) percent_used,
                     fs.largest_chunk,
                     dt.max_extents,
                     dt.extent_management,
                     DECODE(dt.object_count,NULL,0,dt.object_count) object_count
              FROM (SELECT  tablespace_name, 
                            ROUND(SUM(bytes) / 1024 / 1024,   2) mbytes_free,
                            ROUND(MAX(bytes) / 1024 / 1024,   2) largest_chunk
                    FROM dba_free_space
                    GROUP BY tablespace_name ) fs,
                   (SELECT tablespace_name,
                           SUM(bytes)/1024/1024 tblspc_size
                    FROM sys.dba_data_files 
                    GROUP BY tablespace_name) df,
                   (SELECT t.tablespace_name,
                           s.object_count,
                           max_extents,
                           extent_management
                    FROM dba_tablespaces t,
                   (SELECT tablespace_name,
                           COUNT(*)  object_count
                    FROM dba_segments    
                    GROUP BY tablespace_name) s
                   WHERE t.tablespace_name= s.tablespace_name(+)
                   GROUP BY t.tablespace_name,
                            s.object_count,
                            max_extents,
                           extent_management) dt
             WHERE fs.tablespace_name=df.tablespace_name
                   AND dt.tablespace_name = df.tablespace_name 
             ORDER BY var_order_by
          """ ,
'order_by' : 'tablespace_name',
'sortOrder' : 'ASC',
'selectionSource' : 'FreeSpace',
'selectMode' : 'single',
'command' : 'getTablespaceDataFiles',
'outputProgram' : gNOTEPAD,
'outputFile' : 'free_space.txt',
'outputColumns' : [0,1,2,3,4,5,6]
},
{'name': 'DML_Locks', 
 'hlist': 'hlstLocks',
 'window': 'winLocks',
 'title': 'DML Locks',
 'columns': [('osuser', 'OSUser'), ('username', 'Username'),
             ('sid', 'SID'), ('serial#', 'Serial#'),
             ('terminal', 'Terminal'), ('tbl', 'Object Locked'),
             ('lmode', 'Lock Mode Held'), ('ctime', 'Time Locked (Mins)'),
             ('request', 'Lock Mode Requested'), ('type', 'Lock Type')],
'query': """ SELECT ses.osuser,
          NVL(ses.username,'Internal') username, 
          lck.sid sid,
          ses.serial# serial#, 
          NVL(ses.terminal,'None') terminal,
          usr.name||'.'||SUBSTR(obj.name,1,30) tbl, 
          DECODE(lck.lmode,1,'No Lock', 
                   2,'Row Share', 
                   3,'Row Exclusive', 
                   4,'Share', 
                   5,'Share Row Exclusive', 
                   6,'Exclusive',
                   NULL) lmode, 
          ROUND(lck.ctime / 60,   2) ctime,
          DECODE(lck.request,1,'No Lock', 
                     2,'Row Share', 
                     3,'Row Exclusive', 
                     4,'Share', 
                     5,'Share Row Exclusive', 
                     6,'Exclusive',
                 NULL) request  ,
          DECODE(lck.TYPE,'BL','Buffer hash table', 
                  'CF','Control File Transaction', 
                  'CI','Cross Instance Call', 
                  'CS','Control File Schema', 
                  'CU','Bind Enqueue', 
                  'DF','Data File', 
                  'DL','Direct-loader index-creation', 
                  'DM','Mount/startup db primary/secondary instance', 
                  'DR','Distributed Recovery Process', 
                  'DX','Distributed Transaction Entry', 
                  'FI','SGA Open-File Information', 
                  'FS','File Set', 
                  'IN','Instance Number', 
                  'IR','Instance Recovery Serialization', 
                  'IS','Instance State', 
                  'IV','Library Cache InValidation', 
                  'JQ','Job Queue', 
                  'KK','Redo Log 'Kick'', 
                  'LS','Log Start/Log Switch', 
                  'MB','Master Buffer hash table', 
                  'MM','Mount Definition', 
                  'MR','Media Recovery', 
                  'PF','Password File', 
                  'PI','Parallel Slaves', 
                  'PR','Process Startup', 
                  'PS','Parallel Slaves Synchronization', 
                  'RE','USE_ROW_ENQUEUE Enforcement', 
                  'RT','Redo Thread', 
                  'RW','Row Wait', 
                  'SC','System Commit Number', 
                  'SH','System Commit Number HWM', 
                  'SM','SMON', 
                  'SQ','Sequence Number', 
                  'SR','Synchronized Replication', 
                  'SS','Sort Segment', 
                  'ST','Space Transaction', 
                  'SV','Sequence Number Value', 
                  'TA','Transaction Recovery', 
                  'TD','DDL enqueue', 
                  'TE','Extend-segment enqueue', 
                  'TM','DML enqueue', 
                  'TS','Temporary Segment', 
                  'TT','Temporary Table', 
                  'TX','Transaction', 
                  'UL','User-defined Lock', 
                  'UN','User Name', 
                  'US','Undo Segment Serialization', 
                  'WL','Being-written redo log instance', 
                  'WS','Write-atomic-log-switch global enqueue', 
                  'XA','Instance Attribute', 
                  'XI','Instance Registration') as type
      FROM v$lock    lck,  
       v$session ses, 
       sys.user$ usr, 
       sys.obj$  obj 
      WHERE lck.sid = ses.sid 
        AND obj.OBJ# = DECODE(lck.id2,0,lck.id1,lck.id2)  
        AND usr.user# = obj.owner# 
        AND ses.type != 'BACKGROUND' 
     ORDER BY var_order_by
    """,
'order_by': 'osuser',
'sortOrder': 'ASC',
'selectionSource': None,
'selectMode': 'extended',
'command': 'sendToEditor',
'outputProgram': gNOTEPAD,
'outputFile': 'blocking_locks.txt',
'outputColumns': [0,1,2,3,4,5,6,7]
},
{ 'name': 'BlockingLocks',
  'hlist': 'hlstBlockingLocks',
  'window': 'winBlockingLocks',
  'title': 'Blocking Locks',
  'columns': [('osuser_blocking', 'OSUser Blocking'),
            ('username_blocking', 'Username Blocking'),
            ('sid_blocking', 'SID Blocking'),
            ('osuser_waiting', 'OSUser Waiting'),
            ('username_waiting', 'Username Waiting'),
            ('sid_waiting', 'SID Waiting'),
            ('locked_object_id', 'Locked Object ID'),
            ('locked_object_name', 'Locked Object Name'),
            ('locked_object_type', 'Locked Object Type')],
  'query': """SELECT sb.osuser   as osuser_blocking,
           sb.username as username_blocking,   
           sb.sid      as sid_blocking, 
           sb.osuser   as osuser_waiting,
           sw.username as username_waiting, 
           sw.sid      as sid_waiting  ,
           lb.id1      as locked_object_id,
           dbo.object_name as locked_object_name,
           dbo.object_type as locked_object_type
    FROM v$lock lb,
         v$session sb,
         v$lock lw,
         v$session sw,
         dba_objects dbo
    WHERE sb.sid = lb.sid
      AND sw.sid = lw.sid
      AND lb.block = 1
      AND lw.request > 0
      AND lb.id1 = lw.id1
      AND lw.id2 = lw.id2
      AND dbo.object_id = lb.id1 
    """ ,
  'order_by': 'osuser_blocking',
  'sortOrder': 'ASC',
  'selectionSource': None,
  'selectMode': 'extended',
  'command': 'getLockedObject',
  'outputProgram': gNOTEPAD,
  'outputFile': 'locks.txt',
  'outputColumns': [0,1,2,3,4,5]
},
{ 'name' : 'DBA_Registry',
 'hlist' : 'hlstDBARegistry',
 'window' : 'winDBARegistry',
 'title' : 'DBA Registry',
 'columns' : [('comp_id', 'Component ID'), ('comp_name', 'Component Name'),
               ('version', 'Version'), ('status', 'Status'),
               ('modified', 'Date Modified'), ('namespace', 'Namespace'),
               ('control', 'Control'), ('schema', 'Schema'),
               ('procedure', 'Validation Procedure'),
               ('startup', 'Startup'), ('parent_id', 'Parent ID'),
               ('other_schemas', 'Other Schemas')],
 'query' :""" SELECT comp_id,
                comp_name,
                version,
                status,
                modified,
                namespace, 
                control,
                schema,
                procedure,
                startup,
                parent_id,
                other_schemas 
        FROM dba_registry 
        ORDER BY var_order_by
       """,
 'order_by' : 'comp_name',
 'sortOrder' : 'ASC',
 'selectionSource' : 'DBA_Registry',
 'selectMode' : 'extended',
 'command' : 'sendToEditor',
 'outputProgram' : gNOTEPAD,
 'outputFile' : 'table_columns.txt',
 'outputColumns' : [0,1,2,3,4,5,6,7,8,9,10,11]
},
{'name' : 'SysEvents',
 'hlist' : 'hlstSysEvents',
 'window' : 'winSysEvents',
 'title' : 'All System Events',
 'columns' : [('event', 'Event'), ('total_waits', 'Total Waits'),
              ('total_timeouts', 'Total Timeouts'),
              ('time_waited', 'Time Waited (Secs)'),
              ('average_wait', 'Average Wait (Secs)'),
              ('startup_time', 'Startup Time')],
 'query' : """ SELECT e.event,
           e.total_waits,
           e.total_timeouts,
           TO_CHAR((e.time_waited/100),'999,999,999.999') time_waited,
           TO_CHAR((e.average_wait/100),'999,999,999.999')average_wait,
           TO_CHAR(i.startup_time,' Mon-DD-YYYY HH24:MI ')startup_time
    FROM v$system_event e,
         v$instance i  
    ORDER BY var_order_by
    """ ,
 'order_by' : 'event',
 'sortOrder' : 'ASC',
 'selectionSource' : None,
 'selectMode' : 'extended',
 'command' : 'sendToEditor',
 'outputProgram' : gNOTEPAD,
 'outputFile' : 'events.xls',
 'outputColumns' : [0,1,2,3,4,5]
}, 
{'name' : 'SysEventsPercentages',
 'hlist' : 'hlstSysEventsPercentages',
 'window' : 'winSysEventsPercentages',
 'title' : 'System Events Percentages',
 'columns' : [('event', 'Event'), ('total_waits', 'Total Waits'),
             ('pct_waits', 'Pct Waits'), ('time_wait_sec', 'Time Waited Sec'),
             ('pct_time_waited', 'Pct Time Waited'), ('total_timeouts', 'Total Timeouts'),
             ('pct_timeouts', 'Pct Timeouts'), ('average_wait_sec', 'Average Wait Sec')],
 'query' : """SELECT event,
      total_waits,
      ROUND(100 *(total_waits / sum_waits),   2) pct_waits,
      time_wait_sec,
      ROUND(100 *(time_wait_sec / GREATEST(sum_time_waited,   1)),   2) pct_time_waited,
      total_timeouts,
      ROUND(100 *(total_timeouts / GREATEST(sum_timeouts,   1)),   2) pct_timeouts,
      average_wait_sec
    FROM
      (SELECT event,
              total_waits,
              ROUND((time_waited / 100), 2) time_wait_sec,
              total_timeouts,
              ROUND((average_wait / 100), 2) average_wait_sec
       FROM sys.v_$system_event
       WHERE event NOT IN('dispatcher timer',     
                  'i/o slave wait',    
                          'jobq slave wait',  
                  'lock element cleanup',   
                  'Null event',      
                  'parallel query dequeue wait',    
                  'parallel query idle wait - Slaves',    
                  'pipe get', 
                  'PL/SQL lock timer',      
                  'pmon timer',       
                  'rdbms ipc message',   
                  'smon timer',       
                  'SQL*Net break/reset to client',
                  'SQL*Net message from client',     
                  'SQL*Net message to client',    
                  'SQL*Net more data from client', 
                  'virtual circuit status',   
                  'WMON goes to sleep')
         AND event NOT LIKE '%Streams AQ:%'
         AND event NOT LIKE '%done%'
         AND event NOT LIKE '%Idle%' 
         AND event NOT LIKE 'DFS%'
         AND event NOT LIKE 'KXFX%'
       ),
      (SELECT SUM(total_waits) sum_waits,
          SUM(total_timeouts) sum_timeouts,
          SUM(ROUND((time_waited / 100),    2)) sum_time_waited
       FROM sys.v_$system_event
       WHERE event NOT IN('dispatcher timer', 
                  'i/o slave wait',     
                          'jobq slave wait',  
                  'lock element cleanup',   
                  'Null event',      
                  'parallel query dequeue wait',    
                  'parallel query idle wait - Slaves',    
                      'pipe get', 
                  'PL/SQL lock timer',      
                  'pmon timer',       
                  'rdbms ipc message',   
                  'smon timer',       
                  'SQL*Net break/reset to client',
                  'SQL*Net message from client',     
                  'SQL*Net message to client',    
                  'SQL*Net more data from client', 
                  'virtual circuit status',   
                  'WMON goes to sleep')
         AND event NOT LIKE '%Streams AQ:%'
         AND event NOT LIKE '%done%'
         AND event NOT LIKE '%Idle%' 
         AND event NOT LIKE 'DFS%'
         AND event NOT LIKE 'KXFX%'
      )
    ORDER BY var_order_by 
              """,
 'order_by' : 'event',
 'sortOrder' : 'ASC',
 'selectionSource' : None,
 'selectMode' : 'extended',
 'command' : 'sendToEditor',
 'outputProgram' : gNOTEPAD,
 'outputFile' : 'events_summary.xls',
 'outputColumns' : [0,1,2,3,4,5,6,7]
},
{'name' : 'FailedLogins', 
 'hlist' : 'hlstFailedLogins',
 'window' : 'winFailedLogins',
 'title' : 'Failed Login Attempts',
 'columns' : [('failures', '# of Failures'), ('username', 'User Name'),
              ('terminal', 'Terminal'), ('logon_time', 'Logon Time')],
 'query' :""" SELECT COUNT(*) failures, username,
                     SUBSTR(terminal,1,50) terminal,
                     TO_CHAR(timestamp, 'DD-MON-YYYY Day HH24:MI:SS') logon_time
              FROM dba_audit_session
              WHERE returncode <> 0
                AND timestamp > sysdate -7
              GROUP BY username, terminal,
                       TO_CHAR(timestamp, 'DD-MON-YYYY Day HH24:MI:SS')
              ORDER BY var_order_by
           """,
 'order_by' : 'username',
 'sortOrder' : 'ASC',
 'selectionSource' : None,
 'selectMode' : 'extended',
 'command' : 'sendToEditor',
 'outputProgram' : gNOTEPAD,
 'outputFile' : 'failed_logins.txt',
 'outputColumns' : [0,1,2,3]
},
{'name' : 'InvalidLogins', 
 'hlist' : 'hlstInvalidLogins',
 'window' : 'winInvalidLogins',
 'title' : 'Invalid User Login Attempts',
 'columns' : [('username', 'User Name'), ('terminal', 'Terminal'),
               ('logon_time', 'Logon Time')],
 'query' : """ SELECT username,
                     SUBSTR(terminal,1,50) terminal,
                     TO_CHAR(timestamp,  'DD-MON-YYYY Day HH24:MI:SS') logon_time
               FROM dba_audit_session
               WHERE returncode <> 0
                 AND timestamp > sysdate -7
                 AND NOT EXISTS
                   (SELECT 'x'
                      FROM dba_users
                    WHERE dba_users.username = dba_audit_session.username)
               ORDER BY var_order_by
            """,
 'order_by' : 'username',
 'sortOrder' : 'ASC',
 'selectionSource' : None,
 'selectMode' : 'extended',
 'command' : 'sendToEditor',
 'outputProgram' : gNOTEPAD,
 'outputFile' : 'invalid_logins.txt',
 'outputColumns' : [0,1,2]
},
{ 'name' : 'AlertLogMsgs', 
  'hlist' : 'hlstAlertLogMsgs',
  'window' : 'winAlertLogMsgs',
  'title' : 'Alert Log Messages',
  'columns' : [('timestamp', 'Time Stamp'),
                ('message_text', 'Message')], 
  'query' : """ SELECT TO_CHAR(originating_timestamp,'DD.MON.YYYY HH24:MI:SS')
                       AS timestamp,
                     message_text
                FROM v$alert_log
                WHERE originating_timestamp > SYSDATE - varDays
         """, 
  'order_by' : 'timestamp',
  'sortOrder' : '',
  'selectionSource' : None,
  'selectMode' : 'extended',
  'command' : 'sendToEditor',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'alert.log',
  'outputColumns' : [0,1]
},  
{ 'name' : 'AlertLogErrors', 
  'hlist' : 'hlstAlertLogErrors',
  'window' : 'winAlertLogErrors',
  'title' : 'Alert Log Errors',
  'columns' : [('timestamp', 'Time Stamp'),
             ('message_text', 'Error Message')], 
  'query' : """SELECT to_char(originating_timestamp,'DD.MON.YYYY HH24:MI:SS') 
                    AS timestamp,
                    message_text
               FROM v$alert_log
               WHERE originating_timestamp > SYSDATE - varDays
                 AND (REGEXP_LIKE (message_text, '(ORA-)')
                      OR REGEXP_LIKE (message_text, '(error)'))
          """,
  'order_by' : 'timestamp',
  'sortOrder' : 'ASC',
  'selectionSource' : None,
  'selectMode' : 'extended',
  'command' : 'sendToEditor',
  'outputProgram' : gNOTEPAD,
  'outputFile' : 'alertLogErrors.txt',
  'outputColumns' : [0,1]
}
]




