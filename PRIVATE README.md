# Explication du KxsNetwork <3 

> [!NOTE]
> Temporaire il est en francais pour le moment

## Rest api :
- /getLatestVersion: Return js script ( supportée )

- /online-count: Retourne le nombre de joueur ( supportée )

- /ig-count/:gameId: Donne le nombre de player avec le gameId ( supportée )

- /cors: Un espece de proxy pour les image ect ta captée ( Non supportée )

## WebSocket <3:

### Send by client

- "op":2 ( identify )  | {"op":2,"d":{"username": "Kxspourlavie<3","isVoiceChat": False or True} envoyée au moment de l' "op":10
- "op":1 ( keep alive) | {"op": 1, "d": {}} Envoyée tout les ... ms ( recuperée grace au "op":10 )

### Send by server
