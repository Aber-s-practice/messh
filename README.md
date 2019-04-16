## Install

```bash
git clone https://github.com/abersheeran/messh
sudo mv messh/messh.py /usr/bin/messh && sudo rm -rf messh && sudo chmod +x /usr/bin/messh
```

## How to use

Get help about messh

```bash
messh -h
```

Display all ssh-config in messh

```
messh -l
```

Create ssh connection and auto save it in config list

```
messh -t root@host -p 7878 -n "Myself VPS"
```

Use config by index to create ssh connection

```
messh -t 0
```

Delete config by index(integer)

```
messh -d 0
```

## Security

All config would be write to `/etc/messh.conf` by JSON. **Protect it!**
