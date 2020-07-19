# sans-index-creator
Hacky tools to automatically create a SANS index based off the course pdf files.

## How to use
1) Download course pdf from https://www.sans.org/account/download-materials
2) Remove pdf password through qpdf:
  `qpdf --password=enterpasswordhere -decrypt "InputFilename.pdf" "OutputFilename.pdf"`
3) Convert new pdf to txt:
  `pdftotext unencryptedfile.pdf coursetxt.txt`
4) Create index based off txt file (this can take ~5 minutes because each word is searched for in the full English dictionary):
  `python sans_indexer.py -i coursetxt.txt -o courseindex.txt -n "John Smith"`

Please note that the -n field is used to split the txt into pages, as we use the License name as the page delimiter (it is the only string persistant across pages).

If your course has multiple books, you can combine the indexes created by `sans_indexer.py` into one index with the following command:
`python index_combiner.py index1.txt index2.txt index3.txt > combined_index.txt`. This will create an index which displays both book number and page number of each keyword.

## How Does it Work?
For something to be counted as a "word" (and therefore added to the index), it has to meet certain criteria:
* At least 3 chars once certain characters/phrases are stripped from it
* Not in the English dictionary
* Does not start with number
* Is not a link
