git:
	git add .
	git commit -m "" --allow-empty-message
	git push

flash:
	@echo "Press and hold BOOT, press and release RST, then release BOOT"
	read -p "Press any key to continue"
	esptool erase-flash
	wget https://downloads.circuitpython.org/bin/unexpectedmaker_pros3/en_US/adafruit-circuitpython-unexpectedmaker_pros3-en_US-10.0.3.bin
	esptool write-flash 0 adafruit-circuitpython-unexpectedmaker_pros3-en_US-10.0.3.bin
	read -p "Press RST"

update:
	. .venv/bin/activate
	circup install --auto

mount:
	udisksctl mount -b /dev/sda1

unmount:
	udisksctl unmount -b /dev/sda1

deploy:
	sudo cp -v settings.toml *.py /run/media/$(USER)/CIRCUITPY

convert:
	magick sr24db3a82b18cc.png -compress none -resize 64x32! logo.bmp