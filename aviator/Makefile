git:
	git add .
	git commit -m "" --allow-empty-message
	git push

flash:
	echo "Before flashing, press and hold BOOT, press and release RST, then release BOOT"
	esptool erase-flash
	esptool --port $(ls /dev/ttyACM* | head -1) write-flash 0 adafruit-circuitpython-unexpectedmaker_pros3-en_US-10.0.1.bin
	echo "Press RST"

deploy:
	sudo cp -v *.py /run/media/$(USER)/CIRCUITPY

clean:
	rm -f *.tar.xz *.zip *.bin
	clear

connect:
	screen $(ls /dev/ttyACM* | head -1)