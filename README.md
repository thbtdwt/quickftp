# quickftp
python pyftplib and ftplib wrapper.

project on going...

## Server
Example of server configuration file:
```
ip: 127.0.0.1
port: 12345
ftp_root_dir: <path to ftp root directory>
client_timeout: 5
pem_certificate: <path to pem certificate>

clients:
  - name: <user name>
    password: <md5sum of the user password>
    directory: <path to user dir>

  - name: <user name>
    password: <md5sum of the user password>
    directory: <path to user dir>
```


## Client
Example of client configuration file:
 ```
ip: 127.0.0.1
port: 12345
username: <username>
password: <password>
workspace: <workspace directory> 
```

