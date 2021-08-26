all:
	pyinstaller -F server/main.py -n Server
	pyinstaller -F client/main.py -n Client
