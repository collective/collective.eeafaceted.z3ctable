Changelog
=========


0.5 (unreleased)
----------------

- Nothing changed yet.


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
