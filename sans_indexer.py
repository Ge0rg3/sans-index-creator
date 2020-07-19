#!/usr/bin/env python3
import requests as rq
import argparse
import sys

# Parse input
Usage = ("""{}SANS Txt to Index
Use pdftotext to convert a SANS PDF to a txt file, then generate its index here.
Usage:
\t-i, --input-file: txt file of SANS book.
\t-o, --output-file: file to save new index at.
\t-n, --student-name: full name of student, used to split pages by delimiter.
""")

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input-file", help="txt file of SANS book.")
parser.add_argument("-o", "--output-file", help="output file of index.")
parser.add_argument("-n", "--student-name", help="full name of student.")
options = parser.parse_args(sys.argv[1:])


if not options.input_file:
    exit(Usage.format("Please enter an index file.\n"))

if not options.output_file:
    options.output_file = options.input_file.replace(".pdf", "") + ".txt"

delimeter = "Licensed To: "
if options.student_name:
    delimeter += options.student_name

# Get common english words
common_words = rq.get("https://raw.githubusercontent.com/dwyl/english-words/master/words.txt").text.split("\n")
# function to recursively strip given characters in a word
characters_to_strip = "()'\":,”“‘?;-•’—…[]!"
phrases_to_strip = ["'s", "'re", "'ve", "'t", "[0]", "[1]", "[2]", "[3]", "[4]", "[5]", "[6]"]
def strip_characters(word):
    word_length = len(word)
    word = word.replace("’", "'")
    while True:
        for phrase in phrases_to_strip:
            if word.endswith(phrase):
                word = word[:len(phrase)]
        word = word.strip(characters_to_strip).rstrip(".")
        if len(word) == word_length:
            return word
        else:
            word_length = len(word)

# Check that word should be added to index
def word_is_eligible(word):
    # Length check
    if len(word) < 3:
        return False
    # Starts with number
    if word[0].isdigit():
        return False
    # Not common english word
    if word.lower() in common_words or word.lower() + "s" in common_words:
        return False
    # Not SANS url
    if word.startswith("http://") or word.startswith("https://"):
        return False
    return True

# Get pages in pdf
with open(options.input_file, "r") as f:
    data = f.read()
    pages = data.split(delimeter)[1:]


# Get words per page
index = {} # Stores page number and words on page
total_words = [] # Stores all words said
for page_idx, page in enumerate(pages):
    # Recursively replace whitespace with one singular space
    page = page.replace("\n", " ").replace("\t", " ")
    page_len = len(page)
    while True:
        page = page.replace("  ", " ")
        if len(page) == page_len:
            break
        else:
            page_len = len(page)
    # Trim whitespace
    page = page.strip()
    # Get words
    words = page.split(" ")
    long_words = []
    for word in words:
        # Strip some punctuation
        word = strip_characters(word).lower()
        # If threshhold met, append to index
        if word_is_eligible(word):
            total_words.append(word)
            long_words.append(word)
    index[page_idx] = long_words

# Get result strings
results = []
for word in set(total_words):
    pages_word_is_in = []
    # Get page numbers
    for page in index.keys():
        if word in index[page]:
            pages_word_is_in.append(str(page))

    if len(pages_word_is_in) < 15:
        joined_pagenums = ', '.join(pages_word_is_in)
        # Only append if not page number
        if word != joined_pagenums:
            results.append(f"{word}: {', '.join(pages_word_is_in)}")

# Sort output
results.sort(key=str.casefold)

# Write output to file
with open(options.output_file, "w") as f:
    for result in results:
        f.write(result + "\n")
print(f"Written index to {options.output_file}")