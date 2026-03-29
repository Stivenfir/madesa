<?php

set_time_limit(700);
ini_set('max_execution_time', '700');
ini_set('default_socket_timeout', '700');
require_once 'CONFIG.PHP';

$X=hash("sha256",date("Y-m-d"));
$IDusr     = "";
$salida    = "";
$Operacion = "";
$Valor     = "";
$conn      = false;
$archivo   = fopen("LOG.txt", "a");
$SinRta    = array("radicaedidian","aceptadecldian","levantedcldian"); //El API no esperara a que estos procesos enterguen una respuesta
foreach($_POST as $key=>$value){
    $Operacion=$key;
    $Valor= urldecode($value);
}

function LimpiaString($cadena) {
    $patron = '/^[^a-zA-Z0-9<>[]{}]+|[^a-zA-Z0-9><[]{}"]+$/';
	$S0=preg_replace($patron, '', $cadena);	
	$S1=str_replace("\"","'",$S0);	
	$S0=str_replace("\\","\\\\",$S1);
    $S1=str_replace("\n","\\n",$S0);
    return $S1;
}

function RevisarMensaje($cadena){
	$JSOdata = file_get_contents('MsjSP.json');			
	$ListMsJ = json_decode($JSOdata, true);
	foreach($ListMsJ as $SClve=>$Svl){
		if (strpos($cadena,$SClve) !== false){
			return $Svl;
		}
	}
	return $cadena;
}

if (isset($_SERVER['HTTP_ORIGIN'])) {
    echo "{\"Error\":\"Este es un sistema es solo de consultas y solo permite peticiones bajo ciertas condiciones\"}"; 
    //print_r($_POST);
} else{
    try{
		
		header("Access-Control-Allow-Origin: *");
		header("Access-Control-Allow-Methods: POST");
		header("Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept");
		header('Content-Type: text/html; charset=UTF-8, application/json');
		CONN( "1", "2", "3", "4");
		
		
		if($Operacion == "AdmData"){
			switch($Valor){
				case "USUARIO":
					$salida = "<option value='0'>00000000 - EMPRESA</option>";			
					$query = sqlsrv_query($GLOBALS["conn"], "SELECT id,nit,Nombre FROM [API].[dbo].[EmpresasAPI]",[],["Scrollable" => SQLSRV_CURSOR_FORWARD]);
					while ($fila = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {
						$salida= $salida . "<option value='" .$fila["id"]. "'>" .$fila["nit"]. " - " .$fila["Nombre"]. "</option>";
					}
				break;
				case "METODO":
					$salida = "<option value='0'>00000000 - USUARIO</option>";
					$query = sqlsrv_query($GLOBALS["conn"], "SELECT id,Usr FROM [API].[dbo].[UsuariosAPI]",[],["Scrollable" => SQLSRV_CURSOR_FORWARD]);
					while ($fila = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {
						$salida= $salida . "<option value='" .$fila["id"]. "'>" .$fila["id"]. " - " .$fila["Usr"]. "</option>";
					}
				break;
				case "USUARIOS":
					$query = sqlsrv_query($GLOBALS["conn"], "SELECT id,Usr,Token,Empresa,Activo FROM [API].[dbo].[UsuariosAPI]",[],["Scrollable" => SQLSRV_CURSOR_FORWARD]);
					while ($fila = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {
						$salida= $salida . "<tr><td>" .$fila["Usr"]. "</td><td>" .$fila["Token"]. "</td><td>" .$fila["Empresa"]. "</td><td>" .$fila["Activo"]. "</td><td><button class=\"btn btn-primary\" type=\"button\" onclick=\"Editar(\"" .$fila["id"]. "\")\">EDITAR</button></td><td><button class=\"btn btn-danger\" type=\"button\" onclick=\"Borrar(this)\">BORRAR</button></td></tr>";
					}
				break;
				case "OPERACIONES":
					$query = sqlsrv_query($GLOBALS["conn"], "SELECT ID,NomrbreMetodo,Servidor,BD,PeticionSQL,Usuario FROM [API].[dbo].[Parametrizacion]",[],["Scrollable" => SQLSRV_CURSOR_FORWARD]);
					while ($fila = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {
						$salida= $salida . "<tr><td>" .$fila["NomrbreMetodo"]. "</td><td>" .$fila["Servidor"]. "</td><td>" .$fila["BD"]. "</td><td>" .$fila["PeticionSQL"]. "</td><td>" .$fila["Usuario"]. "</td><td><button class=\"btn btn-primary\" type=\"button\" onclick=\"Editar(\"" .$fila["ID"]. "\")\">EDITAR</button></td><td><button class=\"btn btn-danger\" type=\"button\" onclick=\"Borrar(this)\">BORRAR</button></td></tr>";
					}
				break;
				case "EMPRESAS":
					$query = sqlsrv_query($GLOBALS["conn"], "SELECT id,nit,Nombre FROM [API].[dbo].[EmpresasAPI]",[],["Scrollable" => SQLSRV_CURSOR_FORWARD]);
					while ($fila = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {
						$salida= $salida . "<tr><td>" .$fila["nit"]. "</td><td>" .$fila["Nombre"]. "</td><td><button class=\"btn btn-primary\" type=\"button\" onclick=\"Editar(\"" .$fila["id"]. "\")\">EDITAR</button></td><td><button class=\"btn btn-danger\" type=\"button\" onclick=\"Borrar(this)\">BORRAR</button></td></tr>";
					}
				break;
			}
			
		}
		elseif(isset($_SERVER['HTTP_TK']) and !isset($_SERVER['PHP_AUTH_USER'])){
		
			$query = sqlsrv_query($GLOBALS["conn"], "SELECT id FROM [API].[dbo].[UsuariosAPI] WHERE Token='" .$_SERVER['HTTP_TK']. "'",[],["Scrollable" => SQLSRV_CURSOR_FORWARD]);
			fwrite($archivo, $_SERVER['CONTENT_TYPE']." \n\n");
			fwrite($archivo, "SELECT id FROM [API].[dbo].[UsuariosAPI] WHERE Token='" .$_SERVER['HTTP_TK']. "'\n");			
			while ($fila = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {
				$IDusr=$fila["id"];
				fwrite($archivo, $fila["id"]. "\n");
			}
			fwrite($archivo, $Operacion. "\n");
			fwrite($archivo, "SELECT TOP(1) Servidor,BD,PeticionSQL FROM [API].[dbo].[Parametrizacion] WHERE Usuario='" .$IDusr. "' AND NomrbreMetodo='" .$Operacion. "'\n");
			$query = sqlsrv_query($GLOBALS["conn"], "SELECT TOP(1) Servidor,BD,PeticionSQL FROM [API].[dbo].[Parametrizacion] WHERE Usuario='" .$IDusr. "' AND NomrbreMetodo='" .$Operacion. "'",[],["Scrollable" => SQLSRV_CURSOR_FORWARD]);			
			$CNX="";
			$BD="";
			$Consulta="";
			while ($fila = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {
				$CNX=$fila["Servidor"];
				$BD=$fila["BD"];
				$Consulta=$fila["PeticionSQL"];
			}
			sqlsrv_close( $GLOBALS["conn"] );
			CONN($CNX,$BD);        
				 
			$j=0;
			$salida = $salida . '{"data":[';
			$S=str_replace("''", "", $Valor);
			$VALOR=$S;//str_replace("_", " ", $S);		
			$JSOdata = file_get_contents('EXE.json');			
			$CMDs = json_decode($JSOdata, true);
			if (array_key_exists($Consulta,$CMDs)){
				$CMD=$CMDs[$Consulta] ." ". $VALOR;
				fwrite($archivo, "Ejecutable  ::  " .$CMD. "\n -->");
				if (in_array($Consulta,$SinRta)){
					shell_exec($CMD);
					$salida = ("Correcto, proceso ejecutado\n\n");
				}
				else{
					$output = shell_exec($CMD);
					$salida = $output;					
				}			
				fwrite($archivo, $salida);
			}elseif ($Consulta == 'cp2abc') {
				$DecoTXT = base64_decode($VALOR);
				$V=explode("\\",$DecoTXT);
				$a2ABC = fopen("src\\CP2ABC\\ARCHIVOS\\".end($V).".TXT", "w");
				fwrite($a2ABC, $DecoTXT);
				fclose($a2ABC);
				$salida=("Archivo procesado para ser guardado en la ruta especificada");
			}else{
				fwrite($archivo, $CNX. "\n -->");
				fwrite($archivo, $BD. "\n -->");	
				fwrite($archivo, $VALOR. "\n -->");	
				fwrite($archivo, $Consulta . " " .$VALOR. "\n -->");
				$query = sqlsrv_query($GLOBALS["conn"], $Consulta . " " .$VALOR,[],["Scrollable" => SQLSRV_CURSOR_FORWARD]);
				if($query==false){
					//fwrite($archivo, json_encode(sqlsrv_errors()). "\n\n\n");
					echo die(print_r(sqlsrv_errors(), true));
				}
				else{
					while ($fila = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {  
						$i=0;
						if ($j>0){$salida = $salida . ",";}
						$salida = $salida . '{';
						foreach($fila as $key=>$value){
							if ($i>0){$salida = $salida . ",";}
							if (!is_a($value, 'DateTime')){
								$S=LimpiaString($value);
								//$S=$value;
								//$salida=$salida . '"'.$key.'":"'.str_replace(" ","_",$S).'"';
								//$salida=$salida . '"'.$key.'":"'.urldecode($S).'"';
								$salida=$salida . '"'.$key.'":"'.$S.'"';
							}
							else{                        
								$fecha = (is_null($value)) ? "----/--/-- --:--:--" : $value -> format("Y-m-d H:i:s");
								$salida=$salida . '"'.$key.'":"'.$fecha.'"';                        
							}
							$i++;                    
						}
						$salida = $salida . '}';
						$j++;
					}
					$salida = $salida . ']}';
					sqlsrv_close( $GLOBALS["conn"] );
				}
				
			}
				
			
		}elseif(isset($_SERVER['PHP_AUTH_USER']) and isset($_SERVER['PHP_AUTH_PW'])){
			
			$query = sqlsrv_query($GLOBALS["conn"], "SELECT Token FROM [API].[dbo].[UsuariosAPI] WHERE Usr='" .$_SERVER['PHP_AUTH_USER']. "' AND Psw='" .$_SERVER['PHP_AUTH_PW']. "'",[],["Scrollable" => SQLSRV_CURSOR_FORWARD]);
			if($query == false){
				echo die(print_r(sqlsrv_errors(), true));
			}
			else{
				$token="";
				while ($row = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {
					$token=$row["Token"];
				}
				$salida =(strlen($token)==0) ? "{\"error\":\"Revisar Credenciales\"}" : $token;
				//$salida = (strlen($token)==0) ? "{\"error\":\"Revisar Credenciales\"}" . "SELECT Token FROM [API].[dbo].[UsuariosAPI] WHERE Usr='" .$_SERVER['PHP_AUTH_USER']. "' AND Psw='" .$_SERVER['PHP_AUTH_PW']. "'" : $token;
			}			
			
		}
		else{        
			$salida = "{\"Error\":\"Revisar parametrizacion...\"}";        
		}
		
	}
	catch(Exception $e){
		/* foreach (sqlsrv_errors() as $E) {
            fwrite($archivo, "$E \n\n");
        }
        fclose($archivo); */
		$salida = "{\"Error\":\"Revisar parametrizacion.\"}";  
	}    
	fwrite($archivo, utf8_encode($salida). "\n\n###################################################\n\n\n\n");
	fclose($archivo);
    echo utf8_encode($salida);
}

?>