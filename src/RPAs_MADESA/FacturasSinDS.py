import pyodbc
from json import loads

cnxn = pyodbc.connect("DRIVER={SQL Server};SERVER=172.16.10.16\\DBABC21;UID=Operativo;PWD=Repecev2019*")
C = cnxn.cursor()

# SQLPet="""
# SELECT	[BotAbc].[dbo].[tfact_ApiProcesos].[id],[BotAbc].[dbo].[tfact_ApiProcesos].[JsonFact],[BotAbc].[dbo].[tfact_ApiAdjuntos].[id_api]
# FROM	[BotAbc].[dbo].[tfact_ApiProcesos] INNER JOIN [BotAbc].[dbo].[tfact_ApiAdjuntos] ON 
# 		[BotAbc].[dbo].[tfact_ApiProcesos].[id]=[BotAbc].[dbo].[tfact_ApiAdjuntos].[id_factura]
# WHERE	[BotAbc].[dbo].[tfact_ApiProcesos].[Created]>'30/05/2025' AND
# 		([BotAbc].[dbo].[tfact_ApiProcesos].[NitTercero]='901834064' OR [BotAbc].[dbo].[tfact_ApiProcesos].[NitTercero]='860031028') AND
# 		([BotAbc].[dbo].[tfact_ApiProcesos].[Status]='Procesado Ok' OR [BotAbc].[dbo].[tfact_ApiProcesos].[Status]='Recibido Cliente' OR [BotAbc].[dbo].[tfact_ApiProcesos].[Status]='Acusado' OR [BotAbc].[dbo].[tfact_ApiProcesos].[Status]='AD Enviado')

# """

# SQLPet="""
# SELECT	[BotAbc].[dbo].[tfact_ApiProcesos].[id],[BotAbc].[dbo].[tfact_ApiProcesos].[JsonFact],[BotAbc].[dbo].[tfact_ApiAdjuntos].[id_api],[BotAbc].[dbo].[tfact_ApiAdjuntos].[file_name]
# FROM	[BotAbc].[dbo].[tfact_ApiProcesos] INNER JOIN [BotAbc].[dbo].[tfact_ApiAdjuntos] ON 
		# [BotAbc].[dbo].[tfact_ApiProcesos].[id]=[BotAbc].[dbo].[tfact_ApiAdjuntos].[id_factura]
# WHERE	[BotAbc].[dbo].[tfact_ApiProcesos].[Status]='SinAprobar'
# """

SQLPet="""
SELECT TOP(1000)	[BotAbc].[dbo].[tfact_ApiProcesos].[id],[BotAbc].[dbo].[tfact_ApiProcesos].[JsonFact],[BotAbc].[dbo].[tfact_ApiAdjuntos].[id_api],[BotAbc].[dbo].[tfact_ApiAdjuntos].[file_name]
FROM	[BotAbc].[dbo].[tfact_ApiProcesos] INNER JOIN [BotAbc].[dbo].[tfact_ApiAdjuntos] ON 
		[BotAbc].[dbo].[tfact_ApiProcesos].[id]=[BotAbc].[dbo].[tfact_ApiAdjuntos].[id_factura]
ORDER BY [BotAbc].[dbo].[tfact_ApiProcesos].[id] DESC
"""

C.execute(SQLPet)
Data=C.fetchall()
print(f"Cantidad de filas a trabajar  ::  {len(Data)}")
V=[]
for D in Data:
    JSON=loads(D[1])
    if JSON["Documents"]==[]:
        V.append(str(D[0]))
        print(D[0])
print(','.join(V))
