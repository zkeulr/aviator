git:
	git add .
	git commit -m "" --allow-empty-message
	git push

flash:
	echo "Before flashing, press and hold BOOT, press and release RST, then release BOOT"
	esptool --port /dev/ttyACM0 erase-flash
	esptool --port /dev/ttyACM0 write_flash 0 adafruit-circuitpython-unexpectedmaker_pros3-en_US-10.0.1.bin
	echo "Press RST"

transfer:
	sudo mpremote fs cp -r *.py :.

connect:
	screen /dev/ttyACM0