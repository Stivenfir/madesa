from RPAs_MADESA.Bases import Utils

#1. TRAER INFORMACION DE VW_GET_V_INFORMACION_PEDIDOS_MADESA_SHAREPOINT_V2
Utils.cursor.execute("SELECT * FROM VW_GET_V_INFORMACION_PEDIDOS_MADESA_SHAREPOINT_V2 WHERE FechaEnvio=CAST(GETDATE() AS DATE)")
Llaves=[V[0] for V in Utils.cursor.description]
L=len(Llaves)
D={"data":[]}
for F in Utils.cursor.fetchall():#parametrizando cada registro de WMS

    #2. PARAMETRIZAR DATOS DE DESTINO
    D["data"].append({Llaves[i]:F[i] for i in range(0,L)})
    D["data"][-1]["Cliente"]=(D["data"][-1]["Cliente"].split("-"))[-1].strip()
    V = Utils.InfoDepto(D["data"][-1]["Direccion"])
    D["data"][-1]["Departamento"] = V[0]
    D["data"][-1]["Ciudades"]     = V[1]

    #3. PARAMETRIZAR INFO DE LA MERCA
    V_SKUs = D["data"][-1]["SKUs"].split(',') if D["data"][-1]["SKUs"] else ''
    D["data"][-1]["Unidades"]=str(len(V_SKUs))

print(Utils.dumps(D,ensure_ascii=False,default=str))
    
# with open(Utils.os.path.join(Utils.PATH_json,"dataMadesa.json"),'w',encoding="utf-8") as A:
#     A.write(Utils.dumps(D,indent=4,ensure_ascii=False,default=str))