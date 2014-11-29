# tracker.py
# A bittorrent tracker

from socket import inet_aton
from struct import pack

from twisted.web.resource import Resource

from bencode import encode
from simpledb import Database


class TorrentRegistry(object):
    def __init__(self, db_name):
        self.torrents = Database(db_name)

    def add_peer(self, info_hash, peer_id, ip, port):
        """ Add the peer to the torrent database. """

        # If we've heard of this, just add the peer
        if info_hash in self.torrents:
            # Only add the peer if they're not already in the database
            if (peer_id, ip, port) not in self.torrents[info_hash]:
                self.torrents[info_hash].append((peer_id, ip, port))
        # Otherwise, add the info_hash and the peer
        else:
            self.torrents[info_hash] = [(peer_id, ip, port)]

    def peer_list(self, info_hash, compact):
        """ Depending on compact, dispatches to compact or expanded peer
        list functions. """

        peer_list = self.torrents[info_hash]

        if compact:
            # Return a compact peer string, given a list of peer details.
            return b''.join(
                (inet_aton(peer[1]) + pack(">H", int(peer[2])))
                for peer in peer_list)
        else:
            # Return an expanded peer list suitable for the client, given the peer list.
            return [{
                "peer id": peer[0],
                "ip": peer[1],
                "port": int(peer[2]),
            } for peer in peer_list]


class TorrentResource(Resource):
    def __init__(self, db_name='tracker.db', interval=5):
        Resource.__init__(self)
        self.registry = TorrentRegistry(db_name)
        self.interval = interval

    def render_GET(self, request):
        """
        :type request: twisted.web.http.Request
        Take a request, do some some database work, return a peer
        list response. """

        if not all(map(lambda x: x in request.args, ['info_hash', 'compact', 'port', 'peer_id'])):
            self.setResponseCode(403)
            self.finish()
            return
        # Get the necessary info out of the request
        info_hash = request.args['info_hash'][0]
        compact = bool(request.args['compact'][0])
        ip = request.client.host
        port = request.args['port'][0]
        peer_id = request.args['peer_id'][0]

        self.registry.add_peer(info_hash, peer_id, ip, port)

        # Generate a response
        response = {
            "interval": self.interval,
            "complete": 0,
            "incomplete": 0,
            "peers": self.registry.peer_list(info_hash, compact)
        }
        return encode(response)

