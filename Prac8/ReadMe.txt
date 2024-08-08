Install FTP daemon, run the commands:
1. brew install vsftpd
2. sudo mkdir -p /usr/local/etc/vsftpd
3. sudo cp /usr/local/etc/vsftpd/vsftpd.conf.default /usr/local/etc/vsftpd/vsftpd.conf
4. sudo nano /usr/local/etc/vsftpd/vsftpd.conf
5. modify the files:
"listen=YES
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
xferlog_enable=YES
connect_from_port_20=YES
chroot_local_user=YES
allow_writeable_chroot=YES
secure_chroot_dir=/usr/local/var/run/vsftpd/empty
pam_service_name=vsftpd
rsa_cert_file=/usr/local/etc/vsftpd/vsftpd.pem
"
6. sudo mkdir /var/log/vsftpd
7. brew services start vsftpd

/opt/homebrew/etc/vsftpd.conf
ls -l /opt/homebrew/etc/vsftpd.conf

restart servie for homebrew:
sudo launchctl stop homebrew.mxcl.vsftpd
sudo launchctl start homebrew.mxcl.vsftpd

connect to ftp server:
sudo brew services start vsftpd
sudo vsftpd /usr/local/etc/vsftpd.conf

stop connection to ftp server:
sudo brew services stop vsftpd


ncftp ftp.gnu.org


create a new user:
sudo dscl . -create /Users/yi-rou       
sudo dscl . -create /Users/yi-rou UserShell /bin/bash
sudo dscl . -create /Users/yi-rou RealName "Your Full Name"
sudo dscl . -create /Users/yi-rou UniqueID 1001
sudo dscl . -create /Users/yi-rou PrimaryGroupID 1001
sudo dscl . -create /Users/yi-rou NFSHomeDirectory /Users/yi-rou 
sudo dscl . -passwd /Users/yi-rou monica0713
sudo dscl . -append /Groups/admin GroupMembership yi-rou 