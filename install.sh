#!/bin/bash

sudo apt update

install_program(){
#for easy install programs:
#check if program is installed and if not, install it
dpkg -s $1 &>/dev/null
	if [ $? != 0 ] #if program is not installed
		then 
			echo install $1
			sudo apt install $1 -y
			echo $1 installed
	else echo $1 is already installed
fi
}

install_program python3-pip
install_program sqlite3
pip3 install -r requirements.txt

USERNAME=$(logname)
CUR_PATH=$(pwd -P)
NAME="sqlilab"
cat > "$NAME".service <<EOF
[Unit]
Description=$NAME service
After=network.target

[Service]
User=$USERNAME
ExecStart=python3 $CUR_PATH/server.py

[Install]
WantedBy=multi-user.target
EOF


sudo /bin/ln -sf "$CUR_PATH"/"$NAME".service /etc/systemd/system/"$NAME".service

sudo systemctl daemon-reload
sudo systemctl start "$NAME".service
sudo systemctl enable "$NAME".service


