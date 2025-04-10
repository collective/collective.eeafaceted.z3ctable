# encoding: utf-8

from plone.memoize.instance import memoize
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class TestingVocabulary(object):

    @memoize
    def __call__(self, context):
        """ """
        res = []
        res.append(SimpleTerm('existing_key1', 'existing_key1', 'Existing vélue 1'))
        res.append(SimpleTerm('existing_key2', 'existing_key2', 'Existing vélue 2'))
        res.append(SimpleTerm('existing_key3', 'existing_key3', 'Existing vélue 3'))
        return SimpleVocabulary(res)


TestingVocabularyFactory = TestingVocabulary()


@implementer(IVocabularyFactory)
class TestingFullVocabulary(object):

    @memoize
    def __call__(self, context):
        """ """
        res = []
        res.append(SimpleTerm('existing_key1', 'existing_key1', 'Full existing value 1'))
        res.append(SimpleTerm('existing_key2', 'existing_key2', 'Full existing value 2'))
        res.append(SimpleTerm('existing_key3', 'existing_key3', 'Full existing value 3'))
        return SimpleVocabulary(res)


TestingFullVocabularyFactory = TestingFullVocabulary()
