# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.9)

'''Gets genres for imported music based on Last.fm tags.

Uses a provided whitelist file to determine which tags are valid genres.
The included (default) genre list was originally produced by scraping Wikipedia
and has been edited to remove some questionable entries.
The scraper script used is available here:
https://gist.github.com/1241307
'''
import pylast
import codecs
import os
import yaml
import traceback
from beets import plugins
from beets import ui
from beets import config
from beets.util import normpath, plurality
from beets import library
LASTFM = pylast.LastFMNetwork(plugins.LASTFM_KEY, **('api_key',))
PYLAST_EXCEPTIONS = (pylast.WSError, pylast.MalformedResponseError, pylast.NetworkError)
REPLACE = {
    '‐': '-' }

def deduplicate(seq):
    '''Remove duplicates from sequence wile preserving order.
    '''
    seen = set()
    return (lambda .0 = None: [ x for x in .0 if seen.add(x) ])(seq)


def flatten_tree(elem, path, branches):
    '''Flatten nested lists/dictionaries into lists of strings
    (branches).
    '''
    if not path:
        path = []
    if isinstance(elem, dict):
        for k, v in elem.items():
            flatten_tree(v, path + [
                k], branches)
    elif isinstance(elem, list):
        for sub in elem:
            flatten_tree(sub, path, branches)
    else:
        branches.append(path + [
            str(elem)])


def find_parents(candidate, branches):
    '''Find parents genre of a given genre, ordered from the closest to
    the further parent.
    '''
    pass
# WARNING: Decompyle incomplete

WHITELIST = os.path.join(os.path.dirname(__file__), 'genres.txt')
C14N_TREE = os.path.join(os.path.dirname(__file__), 'genres-tree.yaml')

class LastGenrePlugin(plugins.BeetsPlugin):
    
    def __init__(self = None):
        super().__init__()
        self.config.add({
            'whitelist': True,
            'min_weight': 10,
            'count': 1,
            'fallback': None,
            'canonical': False,
            'source': 'album',
            'force': True,
            'auto': True,
            'separator': ', ',
            'prefer_specific': False,
            'title_case': True })
        self.setup()

    
    def setup(self):
        '''Setup plugin from config options
        '''
        if self.config['auto']:
            self.import_stages = [
                self.imported]
        self._genre_cache = { }
        self.whitelist = set()
        wl_filename = self.config['whitelist'].get()
        if wl_filename in (True, ''):
            wl_filename = WHITELIST
        if wl_filename:
            wl_filename = normpath(wl_filename)
            with open(wl_filename, 'rb') as f:
                for line in f:
                    line = line.decode('utf-8').strip().lower()
                    if not line and line.startswith('#'):
                        self.whitelist.add(line)
                    None(None, None, None)
                with None:
                    if not None:
                        pass
        self.c14n_branches = []
        c14n_filename = self.config['canonical'].get()
        self.canonicalize = c14n_filename is not False
        if c14n_filename in (True, ''):
            c14n_filename = C14N_TREE
        elif self.canonicalize and self.config['prefer_specific'].get():
            c14n_filename = C14N_TREE
        if c14n_filename:
            self._log.debug('Loading canonicalization tree {0}', c14n_filename)
            c14n_filename = normpath(c14n_filename)
            with codecs.open(c14n_filename, 'r', 'utf-8', **('encoding',)) as f:
                genres_tree = yaml.safe_load(f)
                None(None, None, None)
            with None:
                if not None:
                    pass
            flatten_tree(genres_tree, [], self.c14n_branches)

    
    def sources(self):
        """A tuple of allowed genre sources. May contain 'track',
        'album', or 'artist.'
        """
        source = self.config['source'].as_choice(('track', 'album', 'artist'))
        if source == 'track':
            return ('track', 'album', 'artist')
        if None == 'album':
            return ('album', 'artist')
        if None == 'artist':
            return ('artist',)

    sources = property(sources)
    
    def _get_depth(self, tag):
        '''Find the depth of a tag in the genres tree.
        '''
        depth = None
        for key, value in enumerate(self.c14n_branches):
            if tag in value:
                depth = value.index(tag)
            
            return depth

    
    def _sort_by_depth(self, tags):
        '''Given a list of tags, sort the tags by their depths in the
        genre tree.
        '''
        depth_tag_pairs = (lambda .0 = None: [ (self._get_depth(t), t) for t in .0 ])(tags)
        depth_tag_pairs = (lambda .0: [ e for e in .0 if e[0] is not None ])(depth_tag_pairs)
        depth_tag_pairs.sort(True, **('reverse',))
        return (lambda .0: [ p[1] for p in .0 ])(depth_tag_pairs)

    
    def _resolve_genres(self, tags):
        '''Given a list of strings, return a genre by joining them into a
        single string and (optionally) canonicalizing each.
        '''
        if not tags:
            return None
        count = None.config['count'].get(int)
        if self.canonicalize:
            tags_all = []
            for tag in tags:
                if self.whitelist:
                    parents = (lambda .0 = None: [ x for x in .0 if self._is_allowed(x) ])(find_parents(tag, self.c14n_branches))
                else:
                    parents = [
                        find_parents(tag, self.c14n_branches)[-1]]
                tags_all += parents
                if self.config['prefer_specific'] and len(tags_all) >= count:
                    pass
                
                tags = tags_all
                tags = deduplicate(tags)
                if self.config['prefer_specific']:
                    tags = self._sort_by_depth(tags)
        tags = (lambda .0 = None: [ self._format_tag(x) for x in .0 if self._is_allowed(x) ])(tags)
        return self.config['separator'].as_str().join(tags[:self.config['count'].get(int)])

    
    def _format_tag(self, tag):
        if self.config['title_case']:
            return tag.title()

    
    def fetch_genre(self, lastfm_obj):
        """Return the genre for a pylast entity or None if no suitable genre
        can be found. Ex. 'Electronic, House, Dance'
        """
        min_weight = self.config['min_weight'].get(int)
        return self._resolve_genres(self._tags_for(lastfm_obj, min_weight))

    
    def _is_allowed(self, genre):
        '''Determine whether the genre is present in the whitelist,
        returning a boolean.
        '''
        if genre is None:
            return False
        if None.whitelist or genre in self.whitelist:
            return True

    
    def _last_lookup(self, entity, method, *args):
        '''Get a genre based on the named entity using the callable `method`
        whose arguments are given in the sequence `args`. The genre lookup
        is cached based on the entity name and the arguments. Before the
        lookup, each argument is has some Unicode characters replaced with
        rough ASCII equivalents in order to return better results from the
        Last.fm database.
        '''
        if any((lambda .0: for s in .0:
not s)(args)):
            return None
        key = None.format(entity, '-'.join((lambda .0: for a in .0:
str(a))(args)))
        if key in self._genre_cache:
            return self._genre_cache[key]
        args_replaced = None
        for arg in args:
            for k, v in REPLACE.items():
                arg = arg.replace(k, v)
            args_replaced.append(arg)
    # WARNING: Decompyle incomplete

    
    def fetch_album_genre(self, obj):
        '''Return the album genre for this Item or Album.
        '''
        return self._last_lookup('album', LASTFM.get_album, obj.albumartist, obj.album)

    
    def fetch_album_artist_genre(self, obj):
        '''Return the album artist genre for this Item or Album.
        '''
        return self._last_lookup('artist', LASTFM.get_artist, obj.albumartist)

    
    def fetch_artist_genre(self, item):
        '''Returns the track artist genre for this Item.
        '''
        return self._last_lookup('artist', LASTFM.get_artist, item.artist)

    
    def fetch_track_genre(self, obj):
        '''Returns the track genre for this Item.
        '''
        return self._last_lookup('track', LASTFM.get_track, obj.artist, obj.title)

    
    def _get_genre(self, obj):
