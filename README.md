Here's a default linuxserver/wireguard client config:

```
[Interface]
Address = 10.13.13.2
PrivateKey = ...
ListenPort = 51820
DNS = 10.13.13.1

[Peer]
PublicKey = ...
PresharedKey = ...
Endpoint = ...:51820
AllowedIPs = 0.0.0.0/0, ::/0
```

The `Interface.Address` needs a `/24` to ensure client can access other IPs normally.
The `Peer.Endpoint` should be changed to a URL if the IP address cannot be guaranteed.
