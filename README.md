# Dataset Preparation for Nuremberg Letterbooks

## Description
- __create-regularised-diplomatic-data.py__: for each letter, creates a page-xml file in the diplomatic-regularised directory with the diplomatic and regularised transcriptions (define paths and collection in ``config.py`` + path to database in ``utils.py`` )
- __config.py__: defines paths for sources and number of collection
- __utils.py__: functions for database handling and reading and writing files etc
- __fix-text-regions.py__: goes through files and removes empty text regions etc if lines were modified or deleted in the sources  
- __page-xml-template.xml__: empty template for page-xml format
