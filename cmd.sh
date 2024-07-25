back=$(pwd)
cd '/mnt/c/Program Files (x86)/PRTG Network Monitor/Custom Sensors/python'
cp iceriver.py $back/custom_sensor
cp antminer.py $back/custom_sensor
cp custom_sensor_lib/ $back/custom_sensor -r
cp images/ $back -r
cp README.md $back -r
cd $back
read txt
if [ "$txt" = 'y' ]
then
	git add .
	git commit -m "Upload Project"
	git push -f
fi
