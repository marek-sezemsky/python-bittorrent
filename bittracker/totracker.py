#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from tornado.web import RequestHandler
from tracker import TorrentRegistry, TorrentRegistryException
from bencode import encode

__author__ = 'viruzzz-kun'
__created__ = '29.11.2014'

log = logging.getLogger('com.tracker')
log.setLevel(logging.DEBUG)


class TorrentHandler(RequestHandler):
    # noinspection PyMethodOverriding
    def initialize(self, database, auto_track=True, interval=30):
        self.registry = TorrentRegistry(database, auto_track)
        self.interval = interval

    def get(self):
        """
        :type request: tornado.httputil.HTTPServerRequest
        Take a request, do some some database work, return a peer
        list response.
        """
        try:
            if not all(map(lambda x: x in self.request.query_arguments, ['info_hash', 'compact', 'port', 'peer_id'])):
                raise TorrentRegistryException('Not all arguments set')
            info_hash = self.get_query_argument('info_hash')
            compact = self.get_query_argument('compact').lower() not in ('0', 'false')
            ip = self.request.remote_ip
            port = int(self.get_query_argument('port'))
            peer_id = self.get_query_argument('peer_id')

            event = self.request.args.get('event', [''])[0]
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