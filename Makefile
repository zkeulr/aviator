git:
	git add .
	git commit -m "$(shell date)"
	git push

program:
	wget https://micropython.org/resources/firmware/ESP32_GENERIC_S3-20250911-v1.26.1.bin
	sudo esptool erase_flash
	esptool --baud 460800 write_flash 0 ESP32_GENERIC_S3-20250911-v1.26.1.bin

clean:
	rm -f *.tar.xz *.zip *.bin
	clear