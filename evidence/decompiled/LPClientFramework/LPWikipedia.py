# Source Generated with Decompyle++
# File: LPWikipedia.pyc (Python 3.9)

'''
Wikipedia-API is easy to use wrapper for extracting information from Wikipedia.

It supports extracting texts, sections, links, categories, translations, etc
from Wikipedia. Documentation provides code snippets for the most common use
cases.
'''
__version__ = (0, 5, 8)
from collections import defaultdict
from enum import IntEnum
import logging
import re
from typing import Any, Dict, List, Optional, Union
from urllib import parse
import requests
import requests_cache
log = logging.getLogger(__name__)
PagesDict = Dict[(str, 'WikipediaPage')]

class ExtractFormat(IntEnum):
    '''Represents extraction format.'''
    WIKI = 1
    HTML = 2


class Namespace(IntEnum):
    '''
    Represents namespace in Wikipedia

    You can gen list of possible namespaces here:

    * https://en.wikipedia.org/wiki/Wikipedia:Namespace
    * https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming

    Currently following namespaces are supported:
    '''
    MAIN = 0
    TALK = 1
    USER = 2
    USER_TALK = 3
    WIKIPEDIA = 4
    WIKIPEDIA_TALK = 5
    FILE = 6
    FILE_TALK = 7
    MEDIAWIKI = 8
    MEDIAWIKI_TALK = 9
    TEMPLATE = 10
    TEMPLATE_TALK = 11
    HELP = 12
    HELP_TALK = 13
    CATEGORY = 14
    CATEGORY_TALK = 15
    PORTAL = 100
    PORTAL_TALK = 101
    PROJECT = 102
    PROJECT_TALK = 103
    REFERENCE = 104
    REFERENCE_TALK = 105
    BOOK = 108
    BOOK_TALK = 109
    DRAFT = 118
    DRAFT_TALK = 119
    EDUCATION_PROGRAM = 446
    EDUCATION_PROGRAM_TALK = 447
    TIMED_TEXT = 710
    TIMED_TEXT_TALK = 711
    MODULE = 828
    MODULE_TALK = 829
    GADGET = 2300
    GADGET_TALK = 2301
    GADGET_DEFINITION = 2302
    GADGET_DEFINITION_TALK = 2303

WikiNamespace = Union[(Namespace, int)]

def namespace2int(namespace = None):
    '''Converts namespace into integer'''
    if isinstance(namespace, Namespace):
        return namespace.value

RE_SECTION = {
    ExtractFormat.HTML: re.compile('\\n? *<h([1-9])[^>]*?>(<span[^>]*></span>)? *(<span[^>]*>)? *(<span[^>]*></span>)? *(.*?) *(</span>)?(<span>Edit</span>)?</h[1-9]>\n?'),
    ExtractFormat.WIKI: re.compile('\\n\\n *(===*) (.*?) (===*) *\\n') }

class Wikipedia:
    '''Wikipedia is wrapper for Wikipedia API.'''
    
    def __init__(self = None, language = None, extract_format = None, headers = ('en', ExtractFormat.WIKI, None, None), cachePath = {
        'language': str,
        'extract_format': ExtractFormat,
        'headers': Optional[Dict[(str, Any)]],
        'cachePath': str,
        'return': None }, **kwargs):
        """
        Constructs Wikipedia object for extracting information Wikipedia.

        :param language: Language mutation of Wikipedia -
                http://meta.wikimedia.org/wiki/List_of_Wikipedias
        :param extract_format: Format used for extractions
                :class:`ExtractFormat` object.
        :param headers:  Headers sent as part of HTTP request
        :param kwargs: Optional parameters used in -
                http://docs.python-requests.org/en/master/api/#requests.request

        Examples:

        * Use proxy: ``Wikipedia('en', proxies={'http': 'http://localhost:1234'})``
        """
        kwargs.setdefault('timeout', 10)
        self.language = language.strip().lower()
        self.extract_format = extract_format
        default_headers = dict() if headers is None else headers
        default_headers.setdefault('User-Agent', 'Wikipedia-API (https://github.com/martin-majlis/Wikipedia-API)')
        self._session = requests_cache.CachedSession(cachePath)
        self._session.headers.update(default_headers)
        self._request_kwargs = kwargs

    
    def __del__(self = None):
        '''Closes session.'''
        self._session.close()

    
    def page(self = None, title = None, ns = None, unquote = (Namespace.MAIN, False)):
        """
        Constructs Wikipedia page with title `title`.

        Creating `WikipediaPage` object is always the first step for extracting
        any information.

        Example::

            wiki_wiki = wikipediaapi.Wikipedia('en')
            page_py = wiki_wiki.page('Python_(programming_language)')
            print(page_py.title)
            # Python (programming language)

            wiki_hi = wikipediaapi.Wikipedia('hi')

            page_hi_py = wiki_hi.article(
                title='%E0%A4%AA%E0%A4%BE%E0%A4%87%E0%A4%A5%E0%A4%A8',
                unquote=True,
            )
            print(page_hi_py.title)
            # पाइथन

        :param title: page title as used in Wikipedia URL
        :param ns: :class:`WikiNamespace`
        :param unquote: if true it will unquote title
        :return: object representing :class:`WikipediaPage`
        """
        if unquote:
            title = parse.unquote(title)
        return WikipediaPage(self, title, ns, self.language, **('title', 'ns', 'language'))

    
    def article(self = None, title = None, ns = None, unquote = (Namespace.MAIN, False)):
        '''
        Constructs Wikipedia page with title `title`.

        This function is an alias for :func:`page`

        :param title: page title as used in Wikipedia URL
        :param ns: :class:`WikiNamespace`
        :param unquote: if true it will unquote title
        :return: object representing :class:`WikipediaPage`
        '''
        return self.page(title, ns, unquote, **('title', 'ns', 'unquote'))

    
    def extracts(self = None, page = None, **kwargs):
        """
        Returns summary of the page with respect to parameters

        Parameter `exsectionformat` is taken from `Wikipedia` constructor.

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bextracts
        - https://www.mediawiki.org/wiki/Extension:TextExtracts#API

        Example::

            import wikipediaapi
            wiki = wikipediaapi.Wikipedia('en')

            page = wiki.page('Python_(programming_language)')
            print(wiki.extracts(page, exsentences=1))
            print(wiki.extracts(page, exsentences=2))

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: summary of the page

        """
        params = {
            'action': 'query',
            'prop': 'extracts',
            'titles': page.title }
        if self.extract_format == ExtractFormat.HTML:
            pass
        elif self.extract_format == ExtractFormat.WIKI:
            params['explaintext'] = 1
            params['exsectionformat'] = 'wiki'
        used_params = kwargs
        used_params.update(params)
        raw = self._query(page, used_params)
        self._common_attributes(raw['query'], page)
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return ''
            return None._build_extracts(v, page)
            return ''

    
    def info(self = None, page = None):
        '''
        https://www.mediawiki.org/w/api.php?action=help&modules=query%2Binfo
        https://www.mediawiki.org/wiki/API:Info
        '''
        params = {
            'action': 'query',
            'prop': 'info',
            'titles': page.title,
            'inprop': '|'.join([
                'protection',
                'talkid',
                'watched',
                'watchers',
                'visitingwatchers',
                'notificationtimestamp',
                'subjectid',
                'url',
                'readable',
                'preload',
                'displaytitle']) }
        raw = self._query(page, params)
        self._common_attributes(raw['query'], page)
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return page
            return None._build_info(v, page)
            return page

    
    def langlinks(self = None, page = None, **kwargs):
        '''
        Returns langlinks of the page with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks
        - https://www.mediawiki.org/wiki/API:Langlinks

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: links to pages in other languages

        '''
        params = {
            'action': 'query',
            'prop': 'langlinks',
            'titles': page.title,
            'lllimit': 500,
            'llprop': 'url' }
        used_params = kwargs
        used_params.update(params)
        raw = self._query(page, used_params)
        self._common_attributes(raw['query'], page)
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return { }
            return None._build_langlinks(v, page)
            return { }

    
    def links(self = None, page = None, **kwargs):
        '''
        Returns links to other pages with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blinks
        - https://www.mediawiki.org/wiki/API:Links

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: links to linked pages

        '''
        params = {
            'action': 'query',
            'prop': 'links',
            'titles': page.title,
            'pllimit': 500 }
        used_params = kwargs
        used_params.update(params)
        raw = self._query(page, used_params)
        self._common_attributes(raw['query'], page)
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return { }
            if None in raw:
                params['plcontinue'] = raw['continue']['plcontinue']
                raw = self._query(page, params)
                v['links'] += raw['query']['pages'][k]['links']
                continue
            return self._build_links(v, page)
            return { }

    
    def backlinks(self = None, page = None, **kwargs):
        '''
        Returns backlinks from other pages with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bbacklinks
        - https://www.mediawiki.org/wiki/API:Backlinks

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: backlinks from other pages

        '''
        params = {
            'action': 'query',
            'list': 'backlinks',
            'bltitle': page.title,
            'bllimit': 500 }
        used_params = kwargs
        used_params.update(params)
        raw = self._query(page, used_params)
        self._common_attributes(raw['query'], page)
        v = raw['query']
        if 'continue' in raw:
            params['blcontinue'] = raw['continue']['blcontinue']
            raw = self._query(page, params)
            v['backlinks'] += raw['query']['backlinks']
            continue
        return self._build_backlinks(v, page)

    
    def categories(self = None, page = None, **kwargs):
        '''
        Returns categories for page with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategories
        - https://www.mediawiki.org/wiki/API:Categories

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: categories for page
        '''
        params = {
            'action': 'query',
            'prop': 'categories',
            'titles': page.title,
            'cllimit': 500 }
        used_params = kwargs
        used_params.update(params)
        raw = self._query(page, used_params)
        self._common_attributes(raw['query'], page)
        pages = raw['query']['pages']
        for k, v in pages.items():
            if k == '-1':
                page._attributes['pageid'] = -1
                return { }
            return None._build_categories(v, page)
            return { }

    
    def categorymembers(self = None, page = None, **kwargs):
        '''
        Returns pages in given category with respect to parameters

        API Calls for parameters:

        - https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bcategorymembers
        - https://www.mediawiki.org/wiki/API:Categorymembers

        :param page: :class:`WikipediaPage`
        :param kwargs: parameters used in API call
        :return: pages in given category
        '''
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': page.title,
            'cmlimit': 500 }
        used_params = kwargs
        used_params.update(params)
        raw = self._query(page, used_params)
        self._common_attributes(raw['query'], page)
        v = raw['query']
        if 'continue' in raw:
            params['cmcontinue'] = raw['continue']['cmcontinue']
            raw = self._query(page, params)
            v['categorymembers'] += raw['query']['categorymembers']
            continue
        return self._build_categorymembers(v, page)

    
    def _query(self = None, page = None, params = None):
        '''Queries Wikimedia API to fetch content.'''
        base_url = 'https://' + page.language + '.wikipedia.org/w/api.php'
        log.info('Request URL: %s', base_url + '?' + '&'.join((lambda .0: [ k + '=' + str(v) for k, v in .0 ])(params.items())))
        params['format'] = 'json'
        params['redirects'] = 1
    # WARNING: Decompyle incomplete

    
    def _build_extracts(self = None, extract = None, page = None):
        '''Constructs summary of given page.'''
        page._summary = ''
        page._section_mapping = defaultdict(list)
        self._common_attributes(extract, page)
        section_stack = [
            page]
        section = None
        prev_pos = 0
        for match in re.finditer(RE_SECTION[self.extract_format], extract['extract']):
            if len(page._section_mapping) == 0:
                page._summary = extract['extract'][0:match.start()].strip()
            elif section is not None:
                section._text = extract['extract'][prev_pos:match.start()].strip()
            section = self._create_section(match)
            sec_level = section.level + 1
            if sec_level > len(section_stack):
                section_stack.append(section)
            elif sec_level == len(section_stack):
                section_stack.pop()
                section_stack.append(section)
            else:
                for _ in range((len(section_stack) - sec_level) + 1):
                    section_stack.pop()
                section_stack.append(section)
            section_stack[len(section_stack) - 2]._section.append(section)
            prev_pos = match.end()
            page._section_mapping[section.title].append(section)
        if page._summary == '':
            page._summary = extract['extract'].strip()
        if prev_pos > 0 and section is not None:
            section._text = extract['extract'][prev_pos:]
        return page._summary

    
    def _create_section(self, match):
        '''Creates section.'''
        sec_title = ''
        sec_level = 2
        if self.extract_format == ExtractFormat.WIKI:
            sec_title = match.group(2).strip()
            sec_level = len(match.group(1))
        elif self.extract_format == ExtractFormat.HTML:
            sec_title = match.group(5).strip()
            sec_level = int(match.group(1).strip())
        section = WikipediaPageSection(self, sec_title, sec_level - 1)
        return section

    
    def _build_info(self = None, extract = None, page = None):
        '''Builds page from API call info.'''
        self._common_attributes(extract, page)
        for k, v in extract.items():
            page._attributes[k] = v
        return page

    
    def _build_langlinks(self = None, extract = None, page = None):
        '''Builds page from API call langlinks.'''
        page._langlinks = { }
        self._common_attributes(extract, page)
        for langlink in extract.get('langlinks', []):
            p = WikipediaPage(self, langlink['*'], Namespace.MAIN, langlink['lang'], langlink['url'], **('wiki', 'title', 'ns', 'language', 'url'))
            page._langlinks[p.language] = p
        return page._langlinks

    
    def _build_links(self = None, extract = None, page = None):
        '''Builds page from API call links.'''
        page._links = { }
        self._common_attributes(extract, page)
        for link in extract.get('links', []):
            page._links[link['title']] = WikipediaPage(self, link['title'], int(link['ns']), page.language, **('wiki', 'title', 'ns', 'language'))
        return page._links

    
    def _build_backlinks(self = None, extract = None, page = None):
        '''Builds page from API call backlinks.'''
        page._backlinks = { }
        self._common_attributes(extract, page)
        for backlink in extract.get('backlinks', []):
            page._backlinks[backlink['title']] = WikipediaPage(self, backlink['title'], int(backlink['ns']), page.language, **('wiki', 'title', 'ns', 'language'))
        return page._backlinks

    
    def _build_categories(self = None, extract = None, page = None):
        '''Builds page from API call categories.'''
        page._categories = { }
        self._common_attributes(extract, page)
        for category in extract.get('categories', []):
            page._categories[category['title']] = WikipediaPage(self, category['title'], int(category['ns']), page.language, **('wiki', 'title', 'ns', 'language'))
        return page._categories

    
    def _build_categorymembers(self = None, extract = None, page = None):
        '''Builds page from API call categorymembers.'''
        page._categorymembers = { }
        self._common_attributes(extract, page)
        for member in extract.get('categorymembers', []):
            p = WikipediaPage(self, member['title'], int(member['ns']), page.language, **('wiki', 'title', 'ns', 'language'))
            p.pageid = member['pageid']
            page._categorymembers[member['title']] = p
        return page._categorymembers

    
    def _common_attributes(extract = None, page = None):
