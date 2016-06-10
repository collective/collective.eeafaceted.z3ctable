# encoding: utf-8

from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm

from plone.memoize.instance import memoize


class TestingVocabulary(object):
    implements(IVocabularyFactory)

    @memoize
    def __call__(self, context):
        """ """
        res = []
        res.append(SimpleTerm('existing_key1', 'existing_key1', 'Existing v\xc3\xa9lue 1'))
        res.append(SimpleTerm('existing_key2', 'existing_key2', 'Existing v\xc3\xa9lue 2'))
        res.append(SimpleTerm('existing_key3', 'existing_key3', 'Existing v\xc3\xa9lue 3'))
        return SimpleVocabulary(res)

TestingVocabularyFactory = TestingVocabulary()


class TestingFullVocabulary(object):
    implements(IVocabularyFactory)

    @memoize
    def __call__(self, context):
        """ """
        res = []
        res.append(SimpleTerm('existing_key1', 'existing_key1', 'Full existing value 1'))
        res.append(SimpleTerm('existing_key2', 'existing_key2', 'Full existing value 2'))
        res.append(SimpleTerm('existing_key3', 'existing_key3', 'Full existing value 3'))
        return SimpleVocabulary(res)

TestingFullVocabularyFactory = TestingFullVocabulary()
