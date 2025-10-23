git:
	git add .
	git commit -m "" --allow-empty-message
	git push

flash:
	read -p "Before flashing, press and hold BOOT, press and release RST, then release BOOT\nPress any key to continue"
	esptool erase-flash
	esptool write-flash 0 adafruit-circuitpython-unexpectedmaker_pros3-en_US-10.0.1.bin
	read -p "Press RST, then open Dolphin and mount board"
	sudo cp -r lib/ /run/media/$(USER)/CIRCUITPY

deploy:
	sudo cp *.py /run/media/$(USER)/CIRCUITPY