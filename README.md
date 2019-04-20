# messh.py

A useful cross-platform SSH configuration manager.

Thanks to [paramiko](https://github.com/paramiko/paramiko/blob/master/demos/interactive.py) for providing cross-platform support.

## Install

In linux

```bash
git clone https://github.com/abersheeran/messh
sudo mv messh/messh.py /usr/bin/messh.py && sudo rm -rf messh && sudo chmod +x /usr/bin/messh.py
```

In windows

```bat
git clone https://github.com/abersheeran/messh
mv messh/messh.py %WINDIR% && rmdir /s /q messh
```

## How to use

Get help about messh

```bash
messh.py -h
```

Display all ssh-config in messh

```
messh.py -l
```

Create ssh connection and auto save it in config list

```
messh.py -t root@host -p 7878 -n "Myself VPS"
```

Use config by index to create ssh connection

```
messh.py -t 0
```

Delete config by index(integer)

```
messh.py -d 0
```

## Security

All config would be write to `/etc/messh.conf` or `%WINDIR%/messh.conf` by JSON. **Protect it!**
