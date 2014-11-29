# tracker.py
# A bittorrent tracker

from socket import inet_aton
from struct import pack

import logging

log = logging.getLogger('com.tracker')
log.setLevel(logging.DEBUG)


class TorrentRegistryException(Exception):
    pass


class TorrentRegistry(object):

    def __init__(self, database, auto_track=True):
        self.torrents = database
        self.auto_track = auto_track

    def add_peer(self, info_hash, peer_id, ip, port):
        """ Add the peer to the torrent database. """
        if not self.is_known_hash(info_hash):
            if self.auto_track:
                self.register_hash(info_hash)
            else:
                raise TorrentRegistryException('Torrent with hash %s is not registered' % info_hash)

        if not self.is_known_peer(info_hash, peer_id, ip, port):
            log.info('Actually adding peer %s to # %s', (peer_id, ip, port), info_hash.encode('hex'))
            self.torrents[info_hash].append((peer_id, ip, port))

    def peer_list(self, info_hash, compact):
        """ Depending on compact, dispatches to compact or expanded peer
        list functions. """

        peer_list = self.torrents.get(info_hash, [])

        if compact:
            # Return a compact peer string, given a list of peer details.
            return b''.join(
                (inet_aton(peer[1]) + pack(">H", peer[2]))
                for peer in peer_list)
        else:
            # Return an expanded peer list suitable for the client, given the peer list.
            return [{
                "peer id": peer[0],
                "ip": peer[1],
                "port": peer[2],
            } for peer in peer_list]

    def is_known_hash(self, info_hash):
        return info_hash in self.torrents

    def is_known_peer(self, info_hash, peer_id, ip, port):
        return (peer_id, ip, port) in self.torrents[info_hash]

    def remove_peer(self, info_hash, peer_id, ip, port):
        if self.is_known_hash(info_hash) and self.is_known_peer(info_hash, peer_id, ip, port):
            log.info('Actually removing peer %s', (peer_id, ip, port))
            self.torrents[info_hash].remove((peer_id, ip, port))

    def register_hash(self, info_hash):
        log.info('Actually adding hash %s', info_hash.encode('hex'))
        if not self.is_known_hash(info_hash):
            self.torrents[info_hash] = []

