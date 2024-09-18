Changelog
=========


2.28 (2024-09-18)
-----------------

- Modified `columns.VocabularyColumn` column by handling multiple ignored_values.
  [sgeulette]
- Improved `colums.DateColumn` column by converting DateTime to compare correctly with ignored_values.
  [sgeulette]
- Python 3 compatibility.
  [gbastien]

2.27 (2024-05-27)
-----------------

- When `the_object=True`, `attrName` may be a callable.
  [gbastien]

2.26 (2023-11-27)
-----------------

- Take into account `VocabularyColumn.ignored_value` in `AbbrColumn`.
  [gbastien]

2.25 (2023-10-27)
-----------------

- In `DateColumn.renderCell`, no need to manage a `DateTime` as it is supported
  by `api.portal.get_localized_time`.
  [gbastien]

2.24 (2023-10-19)
-----------------

- Added `PrettyLinkWithAdditionalInfosColumn.ai_reloaded_fields` functionnality:
  this will force update cached widget and remove its terms if any, this is
  useful when using a context aware vocabulary.
  [gbastien]
- Removed the `PrettyLinkWithAdditionalInfosColumn` `get_ai_xxx` accessors,
  access the attribute directly instead.
  [gbastien]
- Added attribute `BaseColumn.the_object=False`, this means that we are getting
  the information on the object and not on the brain.
  Removed recently added columns `AwakeObjectVocabularyColumn` and
  `AwakeObjectAbbrColumn`, simply use `the_object=True` in this case.
  [gbastien]

2.23 (2023-09-04)
-----------------

- Added `AwakeObjectVocabularyColumn` and `AwakeObjectAbbrColumn`, having same
  behavior as `VocabularyColumn` and `AbbrColumn` but `attrName` is get on awaken
  object instead brain metadata, this avoids adding a `portal_catalog` metadata.
  [gbastien]
- In `AwakeObject` columns, use `imio.helpers.content.base_getattr` instead
  `getattr` to avoid problems with acquisiton.
  [gbastien]

2.22 (2023-08-24)
-----------------

- Rely on `imio.helpers.content.get_user_fullname` that manages fallback to
  `getMemberInfo` if fullname not found in `mutable_properties`.
  This needs to rely on `imio.helpers` that is now a dependency.
  [gbastien]

2.21 (2023-06-27)
-----------------

- In `PrettyLinkWithAdditionalInfosColumn`, in the cached view, update widget
  when it is a `RelationChoice/RelationList` to get correct value.
  [gbastien]

2.20 (2023-06-21)
-----------------

- Corrected iteration problem if gotten value for column is None.
  [sgeulette]

2.19 (2023-02-27)
-----------------

- Extended JS function `toggleCheckboxes` to pass the select/unselect checkbox
  as first parameter and trigger the click event when checkboxes checked or unchecked.
  This changes nothing here but makes this function more useable in other contexts.
  [gbastien]
- JS function `preventDefaultClickTransition` was renamed to
  `preventDefaultClick` in `imio.actionspanel>=1.62`.
  [gbastien]
- Do not break in `I18nColumn` when translating a string with special chars.
  [gbastien]

2.18 (2022-06-14)
-----------------

- Added `BaseColumn.escape = True` so content is escaped.
  Manage escape manually for the `TitleColumn`,  `VocabularyColumn` and the
  `AbbrColumn`, set it to `False` for `CheckBoxColumn`, `ElementNumberColumn`
  and `ActionsColumn` that are entirely generated, set it to `False` for
  `PrettyLinkColumnNothing` as `imio.prettylink` manages it itself.
  [gbastien]

2.17 (2022-05-13)
-----------------

- Doing an unrestricted object get to increase performance.
  [sgeulette]

2.16 (2022-01-03)
-----------------

- Added debug mode when displaying results, this will display the time to
  render each cell, each column (total of every cells) and a global table total.
  Just add `debug=true` to the URL
  [gbastien]

2.15 (2021-11-08)
-----------------

- Renamed parameter passed to `PrettyLinkWithAdditionalInfosColumn.getPrettyLink`
  from `item` to `obj` as it is actually the `obj` that is received and not the `item`.
  [gbastien]
- Added attribute `PrettyLinkWithAdditionalInfosColumn.ai_included_fields`,
  by default it displayed every non empty fields, with this parameter it is
  possible to select which fields to display.
  [gbastien]

2.14 (2021-07-16)
-----------------

- Fixed the `CheckBoxColumn`, add a name to the select all/nothing checkbox so
  it is possible to have several checkbox columns (on same table or when
  displaying several tables on same page).
  [gbastien]

2.13 (2021-01-06)
-----------------

- Added possibility to define a `header_help` message that will be displayed
  when hovering header title.
  [gbastien]
- Added `<label>` tag around input for the `CheckBoxColumn` so it can be syled
  to ease checkbox selection on click.
  [gbastien]

2.12 (2020-10-02)
-----------------

- In `PrettyLinkWithAdditionalInfosColumn`, use IDataManager to get widget value.
  [gbastien]

2.11 (2020-08-18)
-----------------

- Render `DataGridField` in `PrettyLinkWithAdditionalInfosColumn` vertically.
  [gbastien]
- Bugfix in `PrettyLinkWithAdditionalInfosColumn`, sometimes the widget's
  context was the previous row object.
  [gbastien]
- Added parameter `PrettyLinkWithAdditionalInfosColumn.simplified_datagridfield`
  and set it to `False` by default.
  [gbastien]
- Moved `MemberIdColumn.get_user_fullname` out of `MemberIdColumn` so it can be
  easily used from outside.
  [gbastien]
- Added `PrettyLinkWithAdditionalInfosColumn.ai_extra_fields`, that
  let's include extra data not present in schema, by default this will include
  `id`, `UID` and `description`.
  [gbastien]

2.10 (2020-05-08)
-----------------

- In `PrettyLinkWithAdditionalInfosColumn`, removed to setup around current URL
  that was necessary for displaying image and files correctly but instead,
  require `plone.formwidget.namedfile>=2.0.2` that solves the problem.
  [gbastien]

2.9 (2020-02-25)
----------------

- Ignored EMPTY_STRING in VocabularyColumn
  [sgeulette]

2.8 (2020-02-06)
----------------

- Managed correctly a field not yet set.
  [sgeulette]
- In the `PrettyLinkWithAdditionalInfosColumn`, manage `description` manually
  as it is not present in the `@@view` widgets.
  Display it as any other fields if not empty.
  [gbastien]
- Added IconsColumn
  [sgeulette]

2.7 (2019-09-13)
----------------

- In `columns.AbbrColumn`, make sure there is no `'` in tag title or it is not
  rendered correctly in the browser.
  [gbastien]

2.6 (2019-09-12)
----------------

- Fixed translation of `Please select at least one element.` msgid, it was
  still using the old domain `collective.eeafaceted.batchactions` from which
  the `select_row` column was reintegrated.
  [gbastien]
- Optimized the `PrettyLinkWithAdditionalInfosColumn` speed :

  - the `view.update` is called one time and we store the view in the column
    so next rows may use it;
  - use `collective.excelexport` datagridfield exportable to render a
    `datagridfield` because widget rendering is way too slow...
  - added `collective.excelexport` as a dependency.

  [gbastien]

2.5 (2019-08-02)
----------------

- In `VocabularyColumn` and `AbbrColumn`, store the vocabularies instances
  under `_cached_vocab_instance` to avoid doing a lookup for each row.
  This does speed rendering a lot.
  [gbastien]

2.4 (2019-03-28)
----------------

- Fix Date column with SolR result
  [mpeeters]
- Added `ExtendedCSSTable.table_id` and `ExtendedCSSTable.row_id_prefix` making
  it possible to have a CSS id on the table and for each rows.
  By default, we defined it for `FacetedTableView`, `table_id = 'faceted_table'`
  and `row_id_prefix = 'row_'`.
  [gbastien]
- For `ColorColumn`, do not redefine the `renderHeadCell` method but use the
  `header` attribute as we return static content.
  [gbastien]
- Added `BaseColumn.use_caching` attribute set to `True` by default that will
  avoid recomputing a value if it was already computed for a previous row.
  This needs to be managed by column and base `_get_cached_result` and
  `_store_cached_result` are defined on `BaseColumn`.
  Implementations are done for `DateColumn`, `VocabularyColumn` and `AbbrColumn`.
  [gbastien]

2.3 (2018-12-18)
----------------

- In `faceted-table-items.pt`, group `<span>` displaying number of results or
  no results under same `<div>` so it is easy to style.
  [gbastien]

2.2 (2018-11-20)
----------------

- Added `PrettyLinkWithAdditionalInfosColumn.ai_generate_css_class_fields`
  attribute to make it possible to specify fields we want to generate a
  CSS class for, depending on field name and value.  This is useful for
  applying custom CSS to a particular additional info field having a
  specific value.
  [gbastien]

2.1 (2018-09-04)
----------------

- Added `BooleanColumn` based on the `I18nColumn` that displays `Yes` or `No`
  depending on fact that value is `True` or `False`.
  [gbastien]
- Added `PrettyLinkColumn` and `PrettyLinkWithAdditionalInfosColumn` columns
  based on soft dependency to `imio.prettylink`.
  [gbastien]
- Added `ActionsColumn` column based on soft dependency to `imio.actionspanel`.
  [gbastien]
- Added `RelationPrettyLinkColumn` column displaying a relation as a
  pretty link.
  [gbastien]
- Moved overrides of `SequenceTable.renderRow` and `SequenceTable.renderCell`
  relative to being able to define CSS classes by `<td>` tag and depending on
  item value to a separated `ExtendedCSSTable class` so it can be reused by
  other packages.
  [gbastien]

2.0 (2018-06-20)
----------------

- Make widget compatible with `eea.facetednavigation >= 10.0`.
  This makes it no more compatible with older version.
  [gbastien]
- Make package installable on both Plone4 and Plone5.
  [gbastien]
- Reintegrated the `select_row` column from `collective.eeafaceted.batchactions`
  as it is useable by other Faceted packages.
  [gbastien]
- Reintegrated js variables view that manages `no selected elements` message.
  [gbastien]

1.0.3 (2018-05-03)
------------------

- Defined a weight of '100' for the CheckBoxColumn so it is displayed on the
  right of the table columns by default.
  [gbastien]
- Defined correct CSS id for bottom viewlets providers.
  [gbastien]
- Updated french translation of 'Review state' to add a 'E' with accent.
  [gbastien]

1.0.2 (2017-08-03)
------------------

- In BrowserViewCallColumn when computing the path to traverse,
  avoid double '//' that breaks (un)restrictedTraverse.
  [gbastien]
- Make portal and portal_url directly available on the table instance.
  [gbastien]

1.0.1 (2017-06-01)
------------------

- Avoid useless redirects when using sorting and current URL ends with
  `/view` or so.
  [gbastien]
- Fixed tests to use translated strings instead msgid, adapted buildout
  so po files are computed.
  [gbastien]

1.0 (2017-05-31)
----------------

- Check also empty column value with __empty_string__.
  [sgeulette]
- Set default to ignored_value DateColumn
  [sgeulette]

0.19 (2017-02-09)
-----------------

- Enable merging and caching for collective.eeafaceted.z3ctable.js
  in portal_javascripts.
  [gbastien]

0.18 (2017-01-31)
-----------------

- Handle sort_on of the query by storing result of the sorting widget in the
  request.form so it is reuseable by other widget.query that also manage the
  sort_on attribute.
  [gbastien]

0.17 (2016-12-05)
-----------------

- Added ElementNumberColumn that will display the number of the current element
  among elements displayed in the table.  This supports table using batch or not.
  [gbastien]

0.16 (2016-08-03)
-----------------

- Add option ignoreColumnWeight to Table to keep columns ordered as returned by
  setUpColumns() rather than by column weight.
  [sdelcourt]

0.15 (2016-06-13)
-----------------

- Correct wrong release.
  [gbastien]

0.14 (2016-06-13)
-----------------

- ColorColumn : in renderHeadCell, do not return an empty HTML content but `u'&nbsp;&nbsp;&nbsp;'`
  so in case table is too large, the column does not shrink to nothing.
  [gbastien]
- Use `__name__` instead of `attrName` to generate `th_header_` and `td_cell_` CSS classes
  so 2 columns using the same `attrName` get different CSS classes.
  [gbastien]
- Added `AbbrColumn` that will generate a HTML tag `<abbr>` and that is based on 2 vocabularies,
  one that manage the abbreviated value and one that manage the full value.
  [gbastien]

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
