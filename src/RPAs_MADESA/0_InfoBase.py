from RPAs_MADESA.Bases import Utils
import subprocess

Utils.cursorLite.execute("SELECT NombreLista FROM SharePoint_CheckPoint")
NombreLista=Utils.cursorLite.fetchone()[0]

print("1. OBTENIENDO TOKEN")
Salida=subprocess.run(["az.cmd", "account", "get-access-token", "--resource-type", "ms-graph"], capture_output=True, text=True)
D=Utils.loads(Salida.stdout)
TK=D["accessToken"]
Cabecera={"Authorization": f"Bearer " + TK}

print("2. BUSCANDO LA LISTA DE SharePoint")
D=Utils.GraphPet("https://graph.microsoft.com/v1.0/sites/abcstorage.sharepoint.com:/sites/Gestindeentregas",Cabecera)
if "id" not in D:
    print("ERROR consultando el sitio ::")
    print(Utils.dumps(D,indent=4,ensure_ascii=False))
else:
    B=False
    ID_site=D['id']
    D = Utils.GraphPet(f"https://graph.microsoft.com/v1.0/sites/{ID_site}/lists",Cabecera)
    for data in D["value"]:
        if "name" in data and data["name"]==NombreLista:
            B=True
            D=data
            break
    if not B:
        print(f"No se encuentra la lista  '{NombreLista}'  entre la respuesta que dio SharePoint")
    else:
        Utils.cursorLite.execute("UPDATE SharePoint_CheckPoint SET token=?,url=?",(TK,f"https://graph.microsoft.com/v1.0/sites/{ID_site}/lists/{D['id']}/items"))
        Utils.cnxnLite.commit()