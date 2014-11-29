#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twisted.web.resource import Resource
from bencode import encode
from tracker import TorrentRegistry, TorrentRegistryException, log

__author__ = 'viruzzz-kun'
__created__ = '29.11.2014'


class TorrentResource(Resource):
    def __init__(self, database, auto_track=True, interval=30):
        Resource.__init__(self)
        self.registry = TorrentRegistry(database, auto_track)
        self.interval = interval

    def render_GET(self, request):
        """
        :type request: twisted.web.http.Request
        Take a request, do some some database work, return a peer
        list response.
        """
        try:
            if not all(map(lambda x: x in request.args, ['info_hash', 'compact', 'port', 'peer_id'])):
                raise TorrentRegistryException('Not all arguments set')
            info_hash = request.args['info_hash'][0]
            compact = request.args['compact'][0].lower() not in ('0', 'false')
            ip = request.client.host
            port = int(request.args['port'][0])
            peer_id = request.args['peer_id'][0]

            event = request.args.get('event', [''])[0]
            # TODO: process 'started', 'completed' and 'stopped' events
            if event == 'stopped':
                self.registry.remove_peer(info_hash, peer_id, ip, port)
            else:
                self.registry.add_peer(info_hash, peer_id, ip, port)
            return encode({
                "interval": self.interval,
                "complete": 0,
                "incomplete": 0,
                "peers": self.registry.peer_list(info_hash, compact)
            })
        except TorrentRegistryException, e:
            log.error(e.message)
            return encode({
                'failure reason': e.message
            })
        except Exception, e:
            log.error(e.message)
            return encode({
                'failure reason': (u'Internal server error: %s' % unicode(e)).encode('utf-8')
            })