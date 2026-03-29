from RPAs_MADESA.Bases import Utils
from datetime import datetime
print("0. INFORMACION BASE")
Utils.cursorLite.execute("SELECT NumeroPedido FROM InfoPedidos")
Pedidos=[V[0] for V in Utils.cursorLite.fetchall()]

print("1. TRAER INFORMACION DE VW_GET_V_INFORMACION_PEDIDOS_MADESA_SHAREPOINT_V2")
Utils.cursor.execute("SELECT * FROM VW_GET_V_INFORMACION_PEDIDOS_MADESA_SHAREPOINT_V2 WHERE FechaEnvio=CAST(GETDATE() AS DATE)")
Llaves=[V[0] for V in Utils.cursor.description]
L=len(Llaves)
M=Utils.cursor.fetchall()
if not M:
    Utils.cursorLite.execute("DELETE FROM InfoPedidos")
    Utils.cursorLite.execute("DELETE FROM sqlite_sequence WHERE name='InfoPedidos'")
    Utils.cnxnLite.commit()
    print("Aun no hay pedidos en WMS para el dia de hoy")
#BarritaLoading=Utils.tqdm(desc="",total=len(M))
for F in M:#parametrizando cada registro de WMS
    IDPedido=0
    Data={Llaves[i]:F[i] for i in range(0,L)}
    if Data["NumeroPedido"] in Pedidos:
        Utils.LoG.write(f"PEDIDO  {Data['NumeroPedido']}  :: Previamente registrado")
    else:
        V_SKUs    = Data["SKUs"].split(',') if Data["SKUs"] else []
        V_destino = Utils.InfoDepto(Data["Direccion"])
        ID_SharePoint=0
        Data["NumeroPedido"]  = Data["NumeroPedido"].strip()
        Data["Cliente"]       = (Data["Cliente"].split("-"))[-1].strip()
        Data["FechaEnvio"]    = Data["FechaEnvio"].isoformat()
        Data["Unidades"]      = str(len(V_SKUs))
        Data["Peso_KG"]       = str(Data["Peso_KG"])
        Data["Peso_VOL"]      = str(Data["Peso_VOL"])
        Data["Departamento"]  = V_destino[0]
        Data["Ciudades"]      = V_destino[1]
        Data["numero_ruta"]   = str(int(Data['numero_ruta']))
        Data["Observaciones"] = f"{Data['NumeroPedido']} RUTA:"+str(Data["numero_ruta"])
        D={
            "fields":{
                "Cliente_empresa"         : Data["Cliente"],
                "Fecha_envio"             : Data["FechaEnvio"],
                "Numero_pedido"           : Data["NumeroPedido"],
                "Remite"                  : Data["Remite"],
                "Nit"                     : Data["Nit"],
                "Direcci_x00f3_n_destino" : Data["Direccion"],
                "Departamento"            : Data["Departamento"],
                "Ciudades"                : Data["Ciudades"],
                "Barrio"                  : Data["Barrio"],
                "Localidad"               : Data["Localidad"],
                "Telefono_cliente"        : Data["Telefono1"],
                "Unidades"                : Data["Unidades"],
                "SKU"                     : Data["SKUs"],
                "Peso_x0028_KG_x0029_"    : Data["Peso_KG"],
                "Peso_x0028_VOL_x0029_"   : Data["Peso_VOL"],
                "Otro"                    : "NO",
                "Estado"                  : "Creado",
                "Guia"                    : False,
                "Ruta"                    : Data["numero_ruta"],
                "CorreoCliente"           : "sacinternacionalmd@madesa.com",
                "Origen_x002e_"           : Data["Origen"],
                "Destino_x002e_"          : Data["Destino"],
                "Observaciones"           : Data["Observaciones"]
            }
        }
        Rta=Utils.requests.post(Utils.V_Graph[3],headers=Utils.Cabecera,json=D).json()
        Data["Peso_KG"]  = round(float(Data["Peso_KG"]))
        Data["Peso_VOL"] = round(float(Data["Peso_VOL"]))
        if "error" in Rta and Rta["error"]["message"]=="One or more fields with unique constraints already has the provided value.":
            params = {
                "$filter": f"fields/Numero_pedido eq '{Data['NumeroPedido']}'",
                "$select": "id,fields"
            }
            Data["idSharePoint"] = int((Utils.requests.get(Utils.V_Graph[3],headers=Utils.Cabecera,params=params).json())["value"][0]["id"])
            Rta=Utils.GraphPet(f"{Utils.V_Graph[3]}/{ Data['idSharePoint']}?expand=fields",Utils.Cabecera)["fields"]
            if ("Departamento" not in Rta and "Ciudades" not in Rta) or ("Departamento" in Rta and len(Rta["Departamento"])<4) or ("Ciudades" in Rta and len(Rta["Ciudades"])<4):
                Data0={"Departamento":Data["Departamento"],"Ciudades":Data["Ciudades"]}
                Rta=Utils.requests.patch(f"{Utils.V_Graph[3]}/{ Data['idSharePoint']}/fields",headers=Utils.Cabecera,json=Data0)
                #input(Rta.text)
        else:
            Data["idSharePoint"] = int(Rta["id"])
        Utils.cursorLite.execute("INSERT INTO InfoPedidos("+','.join([llave for llave in Data])+") VALUES("+','.join(['?' for i in range(0,len(Data))])+")",tuple(Data[llave] for llave in Data))
        Utils.cnxnLite.commit()
    #BarritaLoading.set_description(f"2. INFORMACION CARGADA (PEDIDO  ::  {Data['NumeroPedido']})")
    #BarritaLoading.update(1)
