
from RPAs_MADESA.Bases import Utils
from datetime import datetime,timedelta

B=True
x1=Utils.Decimal(1000)
x2=Utils.Decimal("0")
x3=Utils.np.uint64(2500000000000)

Url="https://testsomos.tcc.com.co/api/clientes/remesas/grabardespacho8" #Pruebas
#Url="https://somos.tcc.com.co/api/clientes/remesas/grabardespacho8" #Productivo

Datos=Utils.SQLpet1("TCC")
L_Datos=len(Datos)
Utils.LoG.write("\n\n\n\nGENERANGO GUIAS (TCC)\n")
BarritaLoading=Utils.tqdm(desc="Generando GUIAS",total=L_Datos)
for Info in Datos:

    #2. PARAMETRIZAR INFORMACION DEL DESTINATARIO
    FDespacho=(datetime.now()).strftime("%Y-%m-%d")
    V_Destinatario=Info["Cliente"].split(' ')
    match len(V_Destinatario):
        case 1:
            V_Destinatario = [V_Destinatario[0],'','','']
        case 2:
            V_Destinatario = [V_Destinatario[0],'',V_Destinatario[1],'']
        case 3:
            V_Destinatario = [V_Destinatario[0],'',V_Destinatario[1],V_Destinatario[2]]

    #3. PARAMETRIZANDO LA GUIA
    Data={
        "numerodespacho": Info["NumeroPedido"],
        "fechadespacho": FDespacho,
        "solicitudrecogida": {
            "numero": None,
            "fecha": FDespacho,
            "ventanainicio": f"{FDespacho}T14:00:00",
            "ventanafin": f"{FDespacho}T16:00:00"
        },
        "unidadnegocio": "1",
        "cuentaremitente": "1485100", #Pruebas
        #"cuentaremitente": "1625200", #Productivo
        "sederemitente": None,
        "primernombreremitente": "",
        "segundonombreremitente": "",
        "primerapellidoremitente": "",
        "segundoapellidoremitente": "",
        "razonsocialremitente": "ABC CARGO EXPRESS SAS",
        "contactoremitente": "",
        "tipoidentificacionremitente": "NIT",
        "identificacionremitente": "900174994-7",
        "direccionremitente": "AVENIDA CALLE 24 # 95-12  BODEGA 45 PARQUE INDUSTRIAL PORTOS",
        "ciudadorigen": "11001000",
        "telefonoremitente": "3223817102",
        "emailremitente": "EBLANCO@ABCCARGOEXPRESS.COM",
        "destinatarios": [
            {
                "numerocontrol": "1",
                "numeroremesa": None,
                "numeroreferenciacliente": "",
                "tipoidentificaciondestinatario": "CC",
                "identificaciondestinatario": "123456789",
                "sededestinatario": "",
                "primernombredestinatario": V_Destinatario[0],
                "segundonombredestinatario": V_Destinatario[1],
                "primerapellidodestinatario": V_Destinatario[2],
                "segundoapellidodestinatario": V_Destinatario[3],
                "razonsocialdestinatario": Info["Cliente"],
                "contactodestinatario": "",
                "direcciondestinatario": Info["Direccion"],
                "telefonodestinatario": Info["Telefono1"],
                "ciudaddestino": f"{Info['Ciudades']}|{Info['Departamento']}",
                "formapago": "8",
                "llevabodega": "false",
                "recogebodega": "false",
                "centrocostos": "",
                "tiposervicio": "TISE_NORMAL_PAQ",
                #"observaciones": f"{Info['DiceContener']} RUTA 999",
                "observaciones": Info["Observaciones"],
                "recaudoproducto":"0",
                "unidades": [],
                "documentosreferencia": [
                    {
                        "tipodocumento": None,
                        "numerodocumento": None,
                        "fechadocumento": None
                    }
                ]
            }
        ]
    }
    
    # 4. SE AGREGA INFORMCAION DE LAS UNIDADES        
    try:
        ValorTotal=0
        SKUs = Info["SKUs"].split(',')
        for sku in SKUs:
            D_SKUHijo  = Utils.SQLpet2(sku)
            ValorMerca=int(str(D_SKUHijo["Valor"][0]))//1000
            ValorTotal=ValorTotal+ValorMerca
            Data["destinatarios"][0]["unidades"].append({
                "tipounidad": "TIPO_UND_PAQ",
                "tipoempaque": "",
                "claseempaque": "CLEM_GRANDE",
                "dicecontener": sku,
                "kilosreales":    str(int(D_SKUHijo["Peso"][0])//1000).strip(),
                "largo":          str(int(D_SKUHijo["Largo_cm"][0])//1000).strip(),
                "alto":           str(int(D_SKUHijo["Alto_cm"][0])//1000).strip(),
                "ancho":          str(int(D_SKUHijo["Ancho_cm"][0])//1000).strip(),
                "pesovolumen":    "",
                "valormercancia": str(ValorMerca).strip(),
                "codigobarras": "",
                "numerobolsa": "",
                "referencias": "",
                "unidadesinternas": "1"
            })
    except:
        print("\n"+sku)
        print("D_SKUHijo" + D_SKUHijo)
        print(Utils.traceback.format_exc())
        break
    
    #5. GENERANDO LA GUIA
    with open(Utils.os.path.join(Utils.PATH_json,f"TCC_Data_{Info['NumeroPedido']}.json"),'w',encoding="utf-8") as A:
        A.write(Utils.dumps(Data,indent=4,ensure_ascii=False,default=str))
    Rta=Utils.requests.post(Url,json=Data,headers={"AccessToken":"CLITCC20240OLPBZGKAK"}).json() #Pruebas
    #Rta=Utils.requests.post(Url,json=Data,headers={"AccessToken":"BOGABCCARGOEXPR12022026"}).json() #Productivo
    with open(Utils.os.path.join(Utils.PATH_json,f"TCC{Info['NumeroPedido']}.json"),'w',encoding="utf-8") as A:
        A.write(Utils.dumps(Rta,indent=4,ensure_ascii=False))
    if not Rta["remesas"]:
            print(f"\nERROR generando guia para el PEDIDO    {Info['NumeroPedido']}")
            #print({"AccessToken":"CLITCC20240OLPBZGKAK"})
            print(Rta)
    else:
        URLguia=Rta["urlrelacionenvio"].replace(',','')
        Utils.cursorLite.execute("UPDATE InfoPedidos SET Guia=? WHERE id=?",(Rta["remesas"][0]["numeroremesa"],Info["id"]))
        Utils.cnxnLite.commit()
        Data0={"Numero_pedido":Info["NumeroPedido"],"N_x002e_Guia":Rta["remesas"][0]["numeroremesa"],"LinkQuia":URLguia,"Valor_pedido":str(ValorTotal)}
        Rta=Utils.requests.patch(f"{Utils.V_Graph[3]}/{ Info['idSharePoint']}/fields",headers=Utils.Cabecera,json=Data0)
    BarritaLoading.update(1)

##TK Pruebas  ::  CLITCC20240OLPBZGKAK
##TK Prodcuc  ::  BOGABCCARGOEXPR12022026