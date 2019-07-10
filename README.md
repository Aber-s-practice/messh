# messh.py

A useful SSH configuration manager.

## Install

```bash
sudo pip install messh
```

## How to use

Get help about messh

```bash
messh --help
```

Display all ssh-config in messh

```
messh list
```

Create ssh connection and auto save it in config list, use `--only-create` only update config without creating ssh connection.

```
messh connect root@host --port 7878 --name "Myself VPS"
```

Use config by index to create ssh connection

```
messh connect 0
```

Execute command by ssh connection

```
messh execute root@host "ls -l" --port 8080
# or use index
messh execute 0 "ls -l"
```

Delete config by index(integer)

```
messh delete 0
```

## Security

All config would be write to `~/messh.conf` by JSON. **Protect it!**
