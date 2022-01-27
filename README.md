**IMPORTANT**: This is very much a work in progress, excpect I didn't make any progress for over a year now. Most of it works but it's very "ugly" in terms of usability, It would need some work to be deployment-ready. Still, It's been private for a while but iv'e decided to make it public so anyone who might want to improve upon it can do so.
As I remember, it sohuld be compatibale with the Mojang's API, but again, I cannot guaranty anything nor will I be liable to anything bad that might (although shouldn't) happened to you or anyone else while using this repo (including but not limited to getting in trouble with Mojang). You have been warned!

# yggdrasiLDAP
A yggdrasil Server used for Mojang games (Only Minecraft is planned but others should work with little to no modification), All based on LDAP. Which means you can have fake "real" Authentication for closed environments like a home lab network.

# Requirements
1. You need to add your Server's cert to the trust store of the minecraft launcher with
`keytool -importcert -file cert.cer -keystore "C:\Program Files (x86)\Minecraft Launcher\runtime\jre-x64\lib\security\cacerts" -alias "My fake server"`
(Also to the jre keystore which the server is using)

I used the following command and accompanying .conf file to generate the certificate:
```
 openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout cert.key -out cert.cer -extensions 'v3_req' -config cert.conf
 ```
 
 cert.conf:
 ```
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
```

2. You also need to find a way to direct the Minecraft launcher that you are the backend server (use the alt_names on the above snippet). I remember adding an entry to the hosts file, but that could be done with DNS server you control as well, for example.

3. Make sure to have some kind of reverse proxy to handle HTTPS because this code doesn't do it (or modify it to do it). I used some program which I can't seem to recall, but you might be better off using something like Nginx.

4. Lastly, don't forget to modify the parameters  at the start of `app.py` (JWT secret, LDAP server etc.)
