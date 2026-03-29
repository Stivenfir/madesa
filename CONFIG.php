<?php

function CONN($SVR,$DB){
    if ($SVR==="1"){
        $SVR="172.16.10.16";
        $DB="API";
    }
    $Usr="";
    if ($SVR==="172.16.10.16"){
        $Usr="repecev2005";
        $Psw="";
    }
    else{
        $Usr="Operativo";
        $Psw="Repecev2019*";
    }
    $connectionOptions = array("Database" => $DB,"Uid" => $Usr,"PWD" => $Psw);
    $GLOBALS["conn"] = sqlsrv_connect($SVR . "\\DBABC21", $connectionOptions);        
    if ($GLOBALS["conn"] === false) {
        $archivo = fopen("LOG.txt", "a");        
        foreach (sqlsrv_errors() as $E) {
            fwrite($archivo, "Código: " . $E['code'] . "\n");
            fwrite($archivo, "Mensaje: " . $E['message'] . "\n");
            fwrite($archivo, "Estado: " . $E['SQLSTATE'] . "\n\n");
        }
        fclose($archivo);
        die("$SVR : Imposible comunicarse con las BD");
    }     
	else {
		$archivo = fopen("LOG.txt", "a");  
		fwrite($archivo, "Conexión establecida con el servidor $SVR\n\n");
		fclose($archivo);
    }     
}
    
?>