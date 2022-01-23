**IMPORTANT**: This is very much a work in progress, excpect I didn't make any progress for about two years now. Most of it works but it's very "ugly" in terms of usability, It would need some work to be deployment-ready. Still, It's been private for a while but iv'e decided to make it public so anyone who might want to improve upon it can do so.
As I remember, it sohuld be compatibale with the Mojang's API, but again, I cannot guaranty anything nor will I be liable to anything bad that might (although shouldn't) happened to you or anyone else while using this repo (including but not limited to getting in trouble with Mojang). You have been warned!

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
