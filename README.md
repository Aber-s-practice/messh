## Install

```bash
git clone https://github.com/abersheeran/messh
sudo mv messh/messh.py /usr/bin/messh
sudo chmod +x /usr/bin/messh
```

## How to use

```bash
messh -h
```

```
messh -l
```

```
messh -d 0
```

```
messh -t root@host -p 7878 -n "Myself VPS"
```

```
messh -t 0
```

## Security

All config would be write to `/etc/messh.conf` by JSON. **Protect it!**
