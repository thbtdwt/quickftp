# quickftp
This is a python pyftplib and ftplib wrapper.
The goal is to configure ftp server and client
through a configuration file.

## Server
Configuration file:
```
ip: <@ip>
port: <port>
ftp_root_dir: <path to ftp root directory>
client_timeout: <seconds>
pem_certificate: <path to pem certificate>

clients:
  - name: <user name>
    password: <md5sum of the user password>
    directory: <path to user dir>

  - name: <user name>
    password: <md5sum of the user password>
    directory: <path to user dir>
```
Mandatory parameters are "ip", "port", "ftp root dir" and clients list.
Optional parameters are "client timeout" and "pem certificate" 


The server will create a subdirectory for each defined users.

## Client
Client configuration file:
 ```
ip: <@ip>
port: <port>
username: <username>
password: <password>
workspace: <workspace directory> 
```
All parameters are mandatory.


#### API
The client provides 3 main api:
* is_connected() => True is the client is connected to the server.
* is_present(<file path>) => True is the file is present on the server.
* get_file(<file path>) => Get the file from the server.

For a given file when a signature (.md5 or .sha256) is present on the server, the signature file will be automatically downloaded and analyzed. 

## Status
* Server works
* Client works

### Next step
* test pem certificate
* Add "get_directory" api

