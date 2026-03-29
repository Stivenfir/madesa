from RPAs_MADESA.Bases import Utils

V_url=["https://hub.envia.co/olc/","https://hub.envia.co/olc/Seguridad/ingresar/?usuario=6A70BLAN&password=6A70028A","https://hub.envia.co/olc/Seguridad/BannerIngreso","https://hub.envia.co/olc/Guia/ConsultarGuia"]
B=True

if len(Utils.sys.argv)<2 or Utils.sys.argv[1] is None or len(Utils.sys.argv[1])<4:
    print(Utils.SQLpet3())
else:

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

    if not B or "CONSULTAR GUIA {{ titulo }}" not in S:
        Utils.LoG.write(f"Por favor revisa las respuestas generadas por el sitio web (comunmente hospedadas en {Utils.PATH_html})\nSe cancela el proceso.")
        print("{\"Error\":\"Problemas al comunicarse con ENVIA\"}")

    elif Utils.sys.argv[1]=="Rotulos":
        Utils.Sesion.get("https://hub.envia.co/olc/Cola/ColaImpresionA")
        Data={
            'reg': '01',
            'ofi': '001',
            'cta': '15739',
            'cod_usr_mod': '6A70BLAN',
            'okTodasCuentas': False,
            'guiasPorPagina': 100,
        }
        Rta=Utils.Sesion.post("https://hub.envia.co/olc/Cola/ConsultarGuiasColaImpresion/",json=Data)
        with open(Utils.os.path.join(Utils.PATH_json,f"Rotulos.json"),'w',encoding="utf-8") as A:
            A.write(Utils.dumps(Rta.json(),indent=4,ensure_ascii=False,default=str))
        Rta=Utils.Sesion.get("https://hub.envia.co/2IMPRESIONGUIAS/ISticker8x10ExitoRR.aspx?cuenta=01-001-15739&usuario=6A70BLAN")
        #print(Rta.text)
        with open("C:\\xampp\\htdocs\\X_x\\RotulosEnvia.pdf",'wb') as A:
            A.write(Rta.content)
        print(f"http://172.16.10.39/X_x/RotulosEnvia.pdf")

    elif Utils.sys.argv[1]=="RelacionDespacho":
        Utils.Sesion.get("https://hub.envia.co/olc/Cola/ColaImpresionA")
        Data={
            '__VIEWSTATE': '/wEPDwULLTE5NTE0NDg5ODAPZBYCAgMPZBYEAgEPZBYKAgMPFgIeBXZhbHVlBQoyMy8wMi8yMDI2ZAIFDxYCHwAFCjIzLzAyLzIwMjZkAgcPFgIfAAUFMDA6MDBkAgkPFgIfAAUFMjM6NTlkAgsPEA8WBh4NRGF0YVRleHRGaWVsZAUMTm9tX1NlcnZpY2lvHg5EYXRhVmFsdWVGaWVsZAUMQ29kX1NlcnZpY2lvHgtfIURhdGFCb3VuZGdkEBUMCS0gVG9kb3MgLRFET0NVTUVOVE8gRVhQUkVTUw9NRVJDQU5DSUEgQUVSRUETTUVSQ0FOQ0lBIFRFUlJFU1RSRRZSQURJQ0FDSU9OIERFIEZBQ1RVUkFTDkNBREVOQSBERSBGUklPCUVOVklBIEhPWRNlbnZpYSBJTlRFUk5BQ0lPTkFMEkRPQ1VNRU5UT1MgTUFTSVZPUxFlbnZpYSBFTVBSRVNBUklBTA9QQVFVRVRFIEVYUFJFU1MVRE9DVU1FTlRPIEVMRUNUUk9OSUNPFQwBMAExATIBMwE0ATUBNgE3ATgCMTECMTICMTQUKwMMZ2dnZ2dnZ2dnZ2dnZGQCBw8PFgIeBFRleHQFD0RvY3MgYSBEZXZvbHZlcmRkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYOBRRjaGtIYWJpbGl0YVBhcmFtZXRybwURY2hrQ29kX1NlcnZpY2lvJDAFEWNoa0NvZF9TZXJ2aWNpbyQxBRFjaGtDb2RfU2VydmljaW8kMgURY2hrQ29kX1NlcnZpY2lvJDMFEWNoa0NvZF9TZXJ2aWNpbyQ0BRFjaGtDb2RfU2VydmljaW8kNQURY2hrQ29kX1NlcnZpY2lvJDYFEWNoa0NvZF9TZXJ2aWNpbyQ3BRFjaGtDb2RfU2VydmljaW8kOAURY2hrQ29kX1NlcnZpY2lvJDkFEmNoa0NvZF9TZXJ2aWNpbyQxMAUSY2hrQ29kX1NlcnZpY2lvJDExBRJjaGtDb2RfU2VydmljaW8kMTH2ooLwhdo+JUaMEPYwdRIbzcSUi6Lhna2rspxX98qQnw==',
            '__VIEWSTATEGENERATOR': '3A539515',
            'chkCod_Servicio$0': '0',
            'chkCod_Servicio$1': '1',
            'chkCod_Servicio$2': '2',
            'chkCod_Servicio$3': '3',
            'chkCod_Servicio$4': '4',
            'chkCod_Servicio$5': '5',
            'chkCod_Servicio$6': '6',
            'chkCod_Servicio$7': '7',
            'chkCod_Servicio$8': '8',
            'chkCod_Servicio$9': '11',
            'chkCod_Servicio$10': '12',
            'chkCod_Servicio$11': '14',
            'btnContinuar': 'Continuar',
            'esHabilitado': '0',
            'HFCuenta': '',
        }
        P = {
            'Cuenta': '01-001-15739',
            'Usuario': '6A70BLAN',
        }
        Rta=Utils.Sesion.post("https://hub.envia.co/2IMPRESIONGUIAS/RelDespacho_conCB2.aspx",params=P)
        S=Rta.text
        if "No hay informaci" in S:
            print("No hay informacion")
        else:
            with open("C:\\xampp\\htdocs\\X_x\\RelacionDespacho.html",'w',encoding="utf-8") as A:
                A.write(S)
            print(S)

    else:
        
        Resultados={}
        Data=[
            {"guia":Utils.sys.argv[1],"usuario":"6A70BLAN"},
            {"cod_regional":Utils.sys.argv[1][:2],"cod_formapago":Utils.sys.argv[1][2],"cons_guiasu":Utils.sys.argv[1][3:]},
            {"guia":Utils.sys.argv[1]},
            {"cod_regional":Utils.sys.argv[1][:2],"cod_formapago":Utils.sys.argv[1][2],"cons_guiasu":Utils.sys.argv[1][3:]}
        ]
        Cabeceras=["InfoBase","Novedades","Quejas","Citas"]
        URLs=["https://hub.envia.co/olc/Guia/ConsultarGuiaCorporativo/","https://hub.envia.co/olc/Guia/ConsultarNovedadesGuia/","https://hub.envia.co/olc/Guia/ConsultarQuejasGuia/","https://hub.envia.co/olc/Guia/ConsultarCitasGuia/"]
        for i in range(0,len(URLs)):
            try:
                Rta=Utils.Sesion.post(URLs[i],json=Data[i])
                Resultados[Cabeceras[i]]=Rta.json()
            except:
                Resultados[Cabeceras[i]]={}
        print(Utils.dumps(Resultados,ensure_ascii=False,default=str))
        # with open(Utils.os.path.join(Utils.PATH_json,f"Guia_{Utils.sys.argv[1]}.json"),'w',encoding="utf-8") as A:
        #     A.write(Utils.dumps(Resultados,indent=4,ensure_ascii=False))