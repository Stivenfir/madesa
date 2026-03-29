from RPAs_MADESA.Bases import Utils

##TK Pruebas  ::  CLITCC20240OLPBZGKAK
##TK Prodcuc  ::  BOGABCCARGOEXPR12022026
Cabeceras={"AccessToken": "CLITCC20240OLPBZGKAK"}
if len(Utils.sys.argv)<2:
    print(Utils.SQLpet3(Transportadora="TCC"))

elif Utils.sys.argv[1]=="Rotulos":
    D_Guia=Utils.loads(Utils.SQLpet3(Transportadora="TCC"))
    Data={
        "identificacion": "900174994-7",
        "remesas": [str(Info["Guia"]) for Info in D_Guia["data"]]
    }
    Rta=Utils.requests.post("https://testsomos.tcc.com.co/api/clientes/remesas/impresionrotulosv2",headers=Cabeceras,json=Data).json() #Pruebas
    #Rta=Utils.requests.post("https://somos.tcc.com.co/api/clientes/remesas/impresionrotulosv2").json() #Productivo
    print(Rta["UrlRotulosTemporal"])

elif Utils.sys.argv[1]=="RelacionDespachos":
    D_Guia=Utils.loads(Utils.SQLpet3(Transportadora="TCC"))
    Data={
        "identificacion": "900174994-7",
        "remesas": [str(Info["Guia"]) for Info in D_Guia["data"]]
    }
    Rta=Utils.requests.post("https://testsomos.tcc.com.co/api/clientes/remesas/impresionrotulosv2",headers=Cabeceras,json=Data).json() #Pruebas
    #Rta=Utils.requests.post("https://somos.tcc.com.co/api/clientes/remesas/impresionrotulosv2",headers=Cabeceras,json=Data).json() #Productivo
    print(Rta["UrlRelacion"])
    
else:
    JsonData={"remesas": [{"numeroremesa": Utils.sys.argv[1]}],"generarimagen": True}
    Rta=Utils.requests.post("https://testsomos.tcc.com.co/api/clientes/remesas/consultarestatusremesasv3",json=JsonData,headers=Cabeceras).text #Pruebas
    #Rta=Utils.requests.post("https://somos.tcc.com.co/api/clientes/remesas/consultarestatusremesasv3",json=JsonData,headers=Cabeceras).text #Productivo
    print("{data:["+Rta+"]}")