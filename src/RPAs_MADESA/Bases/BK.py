def LeerEXCEL(S):

    Transportadora=S.upper()
    Libro=openpyxl.load_workbook(PATH_xls,read_only=True,data_only=True)
    NmeHoja="Registros"
    Hoja=Libro[NmeHoja]
    b=False
    DatosExcel={"IXs":{},"M":[]}
    Cabeceras=next(Hoja.iter_rows(min_row=1, max_row=1, values_only=True))
    for i in range(0,len(Cabeceras)):
        if Cabeceras[i] is None:
            break
        else:
            DatosExcel["IXs"][Cabeceras[i]]=i
    L_IXs=len(DatosExcel["IXs"])
    L_Filas=int(SoloDigitos(Hoja.calculate_dimension(),Desde=':'))
    BarritaLoading=tqdm(desc=f"Leyendo Filas",total=L_Filas)
    for Fila in Hoja.iter_rows(min_row=2,values_only=True):
        if Fila is None:
            continue
        else:
            Ix=DatosExcel["IXs"]["TRANSPORTADORA"]
            V=[Fila[i] for i in range(0,L_IXs)]
            if V[Ix] is not None and Transportadora in V[Ix].upper():
                DatosExcel["M"].append(V)
            BarritaLoading.update(1)
    return DatosExcel