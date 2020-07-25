scp -r ./* pi@192.168.0.170:dev/PyLights
echo
ssh pi@192.168.0.170 'cd ./dev/PyLights; sudo python3 project.py'
read x