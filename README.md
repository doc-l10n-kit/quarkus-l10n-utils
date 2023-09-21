# quarkus-l10n-utils

Shared utility scripts for quarkus.io localization repositories

## Build site

### Build the localized site

Build the localized quarkus site. The site is saved in the `<L10N_HOME>/docs` directory.

```
<QARKUS_L10N_UTILS_HOME>/bin/build
```

## .po files management

### Update .po files

Upstream source files are updated time to time. This command extract sentences from the source files and update the corresponding .po files.

```
<QARKUS_L10N_UTILS_HOME>/bin/update-po-files
```
### Translate .po files with TMX

Translate .po file entries with tmx, which stores sentences that have previously been translated.

```
<QARKUS_L10N_UTILS_HOME>/bin/translate-po-files-with-tmx
```

### Translate .po files with DeepL API

Translate .po file entries with DeepL API.

```
export TRANSLATOR_DEEPL_APIKEY=<your API key>
<QARKUS_L10N_UTILS_HOME>/bin/translate-po-files-with-deepl
```

### Remove obsolete .po files

Sometime source files are removed in the upstream. This command sweeps the orphaned obsolete .po files.

```
<QARKUS_L10N_UTILS_HOME>/bin/remove-obsolete-po-files
```

## Glossary management

DeepL API offers glossary support, which enables to specify how words and phrases are translated.
These commands help to manage DeepL glossary.

### Create a new glossary

Create a new glossary by uploading `<L10N_HOME>/l10n/glossary/glosary.csv`

```
<QARKUS_L10N_UTILS_HOME>/bin/create-glossary
```

### List glossaries

List glossaries. This can be used to identify glossary id

```
<QARKUS_L10N_UTILS_HOME>/bin/list-glossaries
```

### Delete a glossary

Delete a specified glossary

```
<QARKUS_L10N_UTILS_HOME>/bin/delete-glossary --glossaryId=<glossaryId>
```

