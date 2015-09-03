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
        """Just return a value defined in the REQUEST."""
        res = []
        res.append(SimpleTerm('existing_key1', 'existing_key1', 'Existing value 1'))
        res.append(SimpleTerm('existing_key2', 'existing_key2', 'Existing value 2'))
        res.append(SimpleTerm('existing_key3', 'existing_key3', 'Existing value 3'))
        return SimpleVocabulary(res)

TestingVocabularyFactory = TestingVocabulary()
