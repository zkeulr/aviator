git:
	git add .
	git commit -m "" --allow-empty-message
	git push

flash:
	echo "Before flashing, press and hold BOOT, press and release RST, then release BOOT"
	esptool --port /dev/ttyACM0 erase-flash
	esptool --port /dev/ttyACM0 write_flash 0 UM_PROS3-20250911-v1.26.1.bin
	echo "Press RST"

transfer:
	sudo mpremote fs cp -r *.py :.

connect:
	sudo mpremote connect /dev/ttyACM0

reset:
	sudo mpremote reset