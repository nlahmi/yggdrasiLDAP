# yggdrasiLDAP
A yggdrasil Server used for Mojang games (Only Minecraft is planned but others should work with little to no modification), All based on LDAP. Which means you can have fake "real" Authentication for closed environments like a work network. 


You also need to add your Server's cert to the trust store of the minecraft launcher
keytool -importcert -file C:\Users\n.lahmi\cert.cer -keystore "C:\Program Files (x86)\Minecraft Launcher\runtime\jre-x64\lib\security\cacerts" -alias "My fake server"
(Also to the jre keystore which the server is using)




 openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout cert.key -out cert.cer -extensions 'v3_req' -config cert.conf
 
 [req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = US
ST = VA
L = SomeCity
O = MyCompany
OU = MyDivision
CN = mojang.com
[v3_req]
subjectAltName = @alt_names
[alt_names]
DNS.1 = authserver.mojang.com
DNS.2 = api.mojang.com
DNS.3 = sessionserver.mojang.com
DNS.4 = *.mojang.com
DNS.5 = localhost
DNS.6 = 127.0.0.1