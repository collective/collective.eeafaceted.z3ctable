Changelog
=========


0.13 (2016-06-03)
-----------------

- Display the 'Refresh search results.' link also when there are no current results.
  [gbastien]

0.12 (2016-03-29)
-----------------

- Add english translations.
  [sgeulette]

0.11 (2016-02-15)
-----------------

- Made BrowserViewCallColumn more generic, use unrestrictedTraverse instead of getMultiAdapter
  [sgeulette, gbastien]
- Added DxWidgetRenderColumn to render a dexterity field widget
  [sgeulette]
- Added RelationTitleColumn to render a z3c.relationfield.relation.RelationValue attribute
  [sgeulette]

0.10 (2016-01-15)
-----------------

- Splitted the 2 viewlet managers to be able to add viewlets above and below batch navigation,
  henceforth we have 4 viewlet managers : 'collective.eeafaceted.z3ctable.topabovenav',
  'collective.eeafaceted.z3ctable.topbelownav', 'collective.eeafaceted.z3ctable.bottomabovenav',
  'collective.eeafaceted.z3ctable.bottombelownav'.
  [gbastien]

0.9 (2016-01-04)
----------------

- Use HTML entities &#9650; and &#9660; instead of &blacktriangle; and &blacktriangledown;
  so it behaves nicely in both Firefox and Chrome.
  [gbastien]

0.8 (2015-12-23)
----------------

- Define a default CSS class on each TD as it is already done for TH
  so it is easy to skin if necessary.
  [gbastien]


0.7 (2015-12-17)
----------------

- Replace sort triangle characters by html entities.
  [sgeulette]
- Don't pin setuptools for travis.
  [sgeulette]

0.6 (2015-11-18)
----------------

- Set long_format=True for CreationDateColumn and ModificationDateColumn.
  [gbastien]
- VocabularyColumn: get term by value and not by token.
  [sgeulette]


0.5 (2015-09-28)
----------------

- Added 2 viewlets managers in the table : 'collective.eeafaceted.z3ctable.top'
  and 'collective.eeafaceted.z3ctable.bottom'.
  [gbastien]
- Replaced DateColumn rendering to work not only with DateTime but with DateTime, datetime and date.
  [sgeulette]


0.4 (2015-09-10)
----------------

- If an error occurs during render_table, catch the exception
  and display traceback manually in the Zope log to avoid
  faceted view to be frozen (JS 'lock' the web page and it is not
  unlocked when an error occurs).
  [gbastien]


0.3 (2015-09-03)
----------------

- VocabularyColumn now manage multiValued values (list of values).
  [gbastien]
- Optimized MemberIdColumn by not using getMemberInfo.
  [gbastien]
- Added tests for table and columns.
  [gbastien]
- Added link to refresh the search results.
  [gbastien]
- Manage None value in MemberIdColumn
  [sgeulette]


0.2 (2015-08-04)
----------------

- Fix: avoid UnicodeDecodeErrors in ColorColumn if label contains special chars.
  [gbastien]


0.1 (2015-07-14)
----------------

- Initial release.
  [IMIO]
