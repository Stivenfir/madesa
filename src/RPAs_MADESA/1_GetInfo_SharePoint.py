from RPAs_MADESA.Bases import Utils
from datetime import datetime,timedelta

Hoy=datetime.now().date().strftime("%Y-%m-%d")

Utils.cursorLite.execute("SELECT id,idSharePoint,NumeroPedido,Transportadora FROM InfoPedidos")
M=[[X for X in Y] for Y in Utils.cursorLite.fetchall()]
L=len(M)
if not M:
    print("No hay pedidios")
else:
    #BarritaLoading=Utils.tqdm(desc="RECORRIENDO LISTA",total=L)
    for F in M:
        if F[3] and len(F[3])>2:
            Utils.LoG.write(f"PEDIDO  {F[2]}  :: Ya tiene TRANSPORTADORA\n")
        else:
            Rta=Utils.GraphPet(f"{Utils.V_Graph[3]}/{ F[1]}?expand=fields",Utils.Cabecera)["fields"]
            if "N_x002e_Guia" in Rta and len(Rta["N_x002e_Guia"])>3:
                Utils.cursorLite.execute("UPDATE InfoPedidos SET Guia=?,Transportadora=? WHERE id=?",(Rta["N_x002e_Guia"],(Rta["Transportadora"].upper()).strip(),F[0]))
                Utils.LoG.write(f"PEDIDO  {F[2]}  :: Ya tiene GUIA   {Rta['N_x002e_Guia']}\n")
            if "Transportadora" not in Rta:
                Utils.LoG.write(f"PEDIDO  {F[2]}  :: Sin TRANSPORTADORA\n")
            else:
                F[3]=(Rta["Transportadora"].upper()).strip()
                Utils.cursorLite.execute("SELECT id FROM Transportadoras WHERE Transportadora=?",(F[3],))
                if not Utils.cursorLite.fetchone():
                    Utils.LoG.write(f"PEDIDO  {F[2]}  :: TRANSPORTADORA no valida\n")
                else:
                    Utils.cursorLite.execute("UPDATE InfoPedidos SET Transportadora=? WHERE id=?",(F[3],F[0]))
                    Utils.LoG.write(f"PEDIDO  {F[2]}  ::  OK  TRANSPORTADORA ACTUALIZADA\n")
        #BarritaLoading.update(1)
    try:
        Utils.cnxnLite.commit()
    except:
        print("X.x")
Utils.LoG.close()