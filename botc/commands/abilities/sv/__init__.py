from .curse import Curse
from .dream import Dream

def setup(client):
    client.add_cog(Curse(client))
    client.add_cog(Dream(client))
