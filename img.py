import base64
open_icon = open("Nya-WSL.ico","rb")
b64str = base64.b64encode(open_icon.read())
open_icon.close()
write_data = f"img = {b64str}"
print(write_data)
f = open("icon.py","w+")
f.write(write_data)
f.close()