from RPAs_MADESA.Bases import Utils

B=True
x1=Utils.Decimal(1000)
x2=Utils.Decimal("0")
x3=Utils.np.uint64(2500000000000)
V_url=["https://hub.envia.co/olc/","https://hub.envia.co/olc/Seguridad/ingresar/?usuario=6A70BLAN&password=6A70028A","https://hub.envia.co/olc/Seguridad/BannerIngreso","https://hub.envia.co/olc/Guia/CapturarGuia"]

Datos=Utils.SQLpet1()#Obtener toda la informacion de la merca que no tiene guia en un JSON
L_Datos=len(Datos)
V_SKUs     = [D["SKUs"] for D in Datos]
D_SKUHijo  = Utils.SQLpet2(V_SKUs)
D_SKUHijo["Volumenes"]  = (D_SKUHijo["Ancho_cm"]*D_SKUHijo["Alto_cm"]*D_SKUHijo["Largo_cm"]+x3)//x3#Este es el peso declarado para colocar en la plataforma (Estamos asumiendo que todo es mercancia terrestre)
# with open(Utils.os.path.join(Utils.PATH_txt,f"ListaSKU.txt"),'w',encoding="utf-8") as A:
#     for S in D_SKUHijo["Hijo"]:
#         A.write(S+"\n")
try:
    S=""
    for i in range(0,len(V_url)):
        Rta=Utils.Sesion.get(V_url[i])
        S=Rta.text
        Utils.LoG.write(f"PASO {i}\n")
        if i!=1:
            with open(Utils.os.path.join(Utils.PATH_html,f"{i}.html"),'w',encoding="utf-8") as A:
                A.write(S)
        else:
            D=Utils.loads(S)
            with open(Utils.os.path.join(Utils.PATH_html,f"{i}.json"),'w',encoding="utf-8") as A:
                A.write(Utils.dumps(D,indent=4,ensure_ascii=False))
            if "Nom_Cliente" not in D:
                Utils.LoG.write(f"Problemas para ingresar a la plataforma \n\nPor favor revisar la respuesta enviada por el Servidor ({i}.json)\n\n")
                B=False
                break
except:
    Utils.LoG.write(f"Problemas al navegar en la plataforma\n"+Utils.traceback.format_exc()+"\n\n")
    B=False

if not B or "CAPTURAR GU&#205;A {{ titulo }}" not in S:
    Utils.LoG.write(f"Por favor revisa las respuestas generadas por el sitio web (comunmente hospedadas en {Utils.PATH_html})\nSe cancela el proceso.")
else:

    Utils.LoG.write("\n\n\n\nGENERANGO GUIAS (ENVIA)\n")
    BarritaLoading=Utils.tqdm(desc="Generando GUIAS",total=L_Datos)
    for Info in Datos:

        #1. SE CALCULAN TOTOALES (VOLUMEN DECLARADO  y  VALORES[COP])
        Info["Peso_KG"]=int(Info["Peso_KG"])+(Info["Peso_KG"]>int(Info["Peso_KG"]))
        Info["Valoracion"] = 0
        Info["Peso_VOL"]   = 0
        SKUs         = Info["SKUs"].split(',')
    
        try:
            sku=""
            for X in SKUs:
                sku=X
                Ix=Utils.np.where(sku==D_SKUHijo["Hijo"])[0][0]
                # print(f"PedidoID_{Info['PedidoID']}")
                # print(sku)
                # input(int(D_SKUHijo["Volumenes"][Ix]))
                Info["Valoracion"] = Info["Valoracion"] + int(D_SKUHijo["Valor"][Ix])
                Info["Peso_VOL"]   = Info["Peso_VOL"]   + int(D_SKUHijo["Volumenes"][Ix])
            Info["Valoracion"]     = (Utils.Decimal(int(Info["Valoracion"]))/x1).quantize(x2)
            Info["Peso_VOL"]       = int(Info["Peso_VOL"])
        except:
            print(f"\nNumeroPedido  ::  {Info['NumeroPedido']}\nSKU BUSCADO  ::  {sku}\nLISTA SKU's::")
            for x in D_SKUHijo["Hijo"]:
                print(x)
            print(Utils.traceback.format_exc())
            break

        #2. PARAMETRIZAR INFORMACION DEL DESTINATARIO
        V=(Info["Direccion"].upper()).split(". ")
        if len(V)<2:
            Utils.LoG.write(f"NumeroPedido  {Info['NumeroPedido']}  ::  No se puede extraer la ciudad del cliente  ({Info['Direccion']})")
        else:
            Direccion=" ".join(X for X in V[:-1]) #Obteniendo unformacin de la cliudad
            #input(Direccion)
            V=Utils.InfoDepto(Direccion)#Resultado=[  Depto  ,  Ciudad  ]
            if "BOGOTA" in Direccion:#2. SI EL PASO 1 NO SIRVE....
                V=["CUNDINAMARCA","BOGOTA",13,495]
            elif "SOACHA" in Direccion:
                V=["CUNDINAMARCA","SOACHA",573,13]
            elif "CARTAGENA" in Direccion:
                V=["BOLIVAR","CARTAGENA DE INDIAS",5,167]
            elif "BARRANQUILLA" in Direccion:
                V=["ATLANTICO","BARRANQUILLA",4,136]
            elif " CALI " in Direccion or " CALI " in Direccion or " CALI." in Direccion or "CALI " in S:
                V=["VALLE DEL CAUCA","CALI",30,1065]
            #input(V)
            Data={'cod_pais': '1', 'ciudad': V[1]}
            Rta=Utils.Sesion.post("https://hub.envia.co/olc/Guia/BuscarCiudad",data=Data)
            DataCiudad=(Rta.json())
            if not DataCiudad or V[1]=='':
                Utils.LoG.write(f"NumeroPedido  {Info['NumeroPedido']}  ::  No se puede obtener información de la ciudad ({Data['ciudad']})")
            else:
                DataCiudad=DataCiudad[0]
                Data = {'Ciudad': DataCiudad["Nom_Ciudad"],'DireccionD': Direccion}#Obteniendo información del codigo postal
                Rta=Utils.Sesion.post('https://hub.envia.co/olc/Guia/ConsultarCodigoPostal/', json=Data)
                ZIPCode=Rta.text
                if ZIPCode=='':
                    Utils.LoG.write(f"NumeroPedido  {Info['NumeroPedido']}  ::  No se puede obtener un codigo postal válido  ({ZIPCode})")
                else:

                    #3. GENERANDO LA GUIA
                    Destinatario=(Info["Cliente"].split('-'))[-1]
                    Data = {
                        'ciudad_origen': 'BOGOTA-D.C.',
                        'ciudad_destino': DataCiudad["Cod_Ciudad"],
                        'cod_formapago': '4',
                        'cod_servicio': '3',
                        'mca_nosabado': '0',
                        'mca_docinternacional': '0',
                        'cod_regional_cta': '01',
                        'cod_oficina_cta': '001',
                        'cod_cuenta': '15739',
                        'num_unidades': len(SKUs),
                        'mpesoreal_k': int(Info["Peso_KG"]),
                        'mpesovolumen_k': Info["Peso_VOL"],
                        'valor_declarado': int(Info["Valoracion"]),
                        'con_cartaporte': '0',
                        'info_origen': {
                            'nom_remitente': 'ABC CARGO EXPRESS SAS',
                            'dir_remitente': 'AVENIDA CALLE 24 # 95-12  BODEGA 45 PARQUE INDUSTRIAL PORTOS',
                            'tel_remitente': '4222377',
                            'ced_remitente': '900174994-7',
                            'email_remitente': 'EBLANCO@ABCCARGOEXPRESS.COM',
                        },
                        'info_destino': {
                            'nom_destinatario': Destinatario,
                            'dir_destinatario': Direccion,
                            'tel_destinatario': Info["Telefono1"],
                            'ced_destinatario': '',
                            'email_destinatario': '',
                        },
                        'info_contenido': {
                            'dice_contener': 'P.'+Info["NumeroPedido"],
                            'texto_guia': '',
                            'accion_notaguia': '',
                            'num_documentos': f"RUTA:"+str(Info['numero_ruta'])+"SKU:"+SKUs[0],
                            'centrocosto': '',
                            'valorproducto': '0',
                            'fec_citapactada': None,
                            'fec_venordencompra': None,
                            'ciceg': None,
                        },
                        'numero_guia': '',
                        'Mca_Direccion_Verificada': 1,
                        'mca_arista45': None,
                    }
                    Utils.Sesion.headers.update({'Authorization':'Basic NkE3MEJMQU46NkE3MDAyOEE='})
                    # with open(Utils.os.path.join(Utils.PATH_json,f"PedidoID_{Info['PedidoID']}.json"),'w',encoding="utf-8") as A:
                    #     A.write(Utils.dumps(Datos1,indent=4,ensure_ascii=False))
                    Rta=Utils.Sesion.post("https://hub.envia.co/ServicioLiquidacionREST/Service1.svc/Generacion/",json=Data)
                    DatosGuia=Rta.json()
                    #input(Rta.text)
                    with open(Utils.os.path.join(Utils.PATH_json,f"Envia{Info['NumeroPedido']}.json"),'w',encoding="utf-8") as A:
                        A.write(Utils.dumps(DatosGuia,indent=4,ensure_ascii=False))
                    # with open(Utils.os.path.join(Utils.PATH_json,f"PedidoID_{Info['PedidoID']}.json"),'w',encoding="utf-8") as A:
                    #     A.write(Utils.dumps({"Peticion":Data,"Respuesta":DatosGuia},indent=4,ensure_ascii=False))
                    if DatosGuia["guia"] is not None and len(DatosGuia["guia"])>0:
                        #Utils.cursor.execute("UPDATE InfoPedidos SET Guia=?,PesoCobrado=?,ValorFlete=?,ValorVariable=?,ValorOtros=?,URLGuia=? WHERE PedidoID=?",(DatosGuia["guia"],DatosGuia["k_cobrados"],DatosGuia["valor_flete"],DatosGuia["valor_costom"],DatosGuia["valor_otros"],DatosGuia["urlguia"],Info['PedidoID']))
                        Utils.cursorLite.execute("UPDATE InfoPedidos SET Guia=?,Peso_VOL=? WHERE id=?",(DatosGuia["guia"],DatosGuia["k_cobrados"],Info['id']))
                        Data0={"Numero_pedido":Info["NumeroPedido"],"N_x002e_Guia":DatosGuia["guia"],"LinkQuia":DatosGuia["urlguia"],"Valor_pedido":str(DatosGuia["valor_costom"]),"Flete":DatosGuia["valor_flete"]}
                        Rta=Utils.requests.patch(f"{Utils.V_Graph[3]}/{ Info['idSharePoint']}/fields",headers=Utils.Cabecera,json=Data0)
                        Utils.cnxnLite.commit()
                    else:
                        Utils.LoG.write(f"NumeroPedido  {Info['NumeroPedido']}  ::  No se creo la guia")
                    BarritaLoading.update(1)
                    
Utils.Sesion.get("https://hub.envia.co/olc/")
Utils.Sesion.close()
Utils.LoG.close()