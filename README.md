# messh.py

A useful SSH configuration manager.

## Install

```bash
sudo pip install messh
```

## How to use

Get help about messh

```bash
messh.py --help
```

Display all ssh-config in messh

```
messh.py list
```

Create ssh connection and auto save it in config list

```
messh.py connect root@host --port 7878 --name "Myself VPS"
```

Use config by index to create ssh connection

```
messh.py connect 0
```

Delete config by index(integer)

```
messh.py delete 0
```

## Security

All config would be write to `/etc/messh.conf` by JSON. **Protect it!**
