#!/usr/bin/python3
"""
[`pdf2audio.py`](https://github.com/deangelisdf/write2audiobook/blob/main/pdf2audio.py)

Convert a `.pdf` file to an MP3 file. <experiment>

Usage example:
    `python pdf2audio.py document.pdf en`

!!! warning
    This module is experimental.

"""
import os
import re
import tempfile
import json
from io import BytesIO  # Use BytesIO to create a file-like object
import fitz
from fitz import utils  # PyMuPDF
from fontTools.cffLib import CFFFontSet
from backend_audio import m4b, ffmetadata_generator
from frontend      import input_tool

BACK_END_TTS = m4b.get_back_end_tts()
PATTERN_REFERENCE_STR = r"\[[0-9]+(, [0-9]+)*\]|\([0-9]+(, [a-zA-Z0-9]+)+\)"
REGEX_REFERENCE = re.compile(PATTERN_REFERENCE_STR)

def read_cff(cff_data: dict) -> dict:
    """Decompile CFF fonts.

    Arguments:
        cff_data: The CFF font file's content.

    Returns:
        cff_font_set: The top dictionary from the CFF font file's content.
    """
    cff_data_io = BytesIO(cff_data)
    cff_font_set = CFFFontSet()
    cff_font_set.decompile(cff_data_io, None)
    return cff_font_set.topDictIndex[0]  # Return the top dictionary

def __filter_family_name(family_name:str)->str:
    family_name = family_name.lower().replace('semibold','').replace('italic','')
    family_name = family_name.replace('medium','').replace('bold','').replace('light','')
    family_name = family_name.replace('book', '')
    return family_name.strip()

def __add_family_name(fonts:dict)->dict:
    result = {}
    for font_name, font in fonts.items():
        cfffont = read_cff(font)
        print(cfffont.FamilyName)
        family_name = __filter_family_name(cfffont.FamilyName)
        result[font_name] = {'family-name': family_name}
    return result

def get_fonts(pdf_doc:utils.pymupdf.Document) -> dict:
    """Get the fonts used in the original document.

    Arguments:
        pdf_doc: The original PDF document.

    Returns:
        fonts: A map of font names and their properties.
    """
    xref_visited = []
    fonts = {}
    for page in pdf_doc:
        fl = page.get_fonts() # list of fonts of page
        for f in fl:
            xref = f[0] # xref of font
            if xref in xref_visited:
                continue # skip if already processed
            xref_visited.append(xref) # do not process a second time
            # extract font buffer
            basename, ext, _, buffer = pdf_doc.extract_font(xref)
            if ext == "n/a": # is the font extractable?
                continue
            if xref in fonts:
                print(xref, "is already in fonts")
            print(ext)
            fonts[basename] = buffer
    fonts = __add_family_name(fonts)
    return fonts

def filter_reference(text_with_ref:str)->str:
    """Remove a refence, like a footnote or citation, from a text segment.

    Arguments:
        text_with_ref: The text segment that has a reference.

    Returns:
        result: The text segment without the reference.
    """
    return REGEX_REFERENCE.sub('', text_with_ref)

def get_chapter_text(pdf_doc:utils.pymupdf.Document, pattern_header:str, pattern_footer:str)->list:#pylint: disable=R0914,R1260
    """Get text from a PDF document.

    Arguments:
        pdf_doc: The original PDF document.
        pattern_header: A regular expression pattern that matches the PDF document's header.
        pattern_footer: A regular expression pattern that matches the PDF document's footer.

    Returns:
        extracted_text: The PDF document's content.
    """
    extracted_text = []
    block_prediction = ""
    prev_font = None
    regex_header = re.compile(pattern_header)
    regex_footer = re.compile(pattern_footer)
    for page_num in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    font_name = span["font"]
                    font_size = span["size"]
                    if (prev_font is not None) and (prev_font == (font_name, font_size)):
                        block_prediction += span["text"]
                        continue
                    if regex_footer.match(block_prediction) or regex_header.match(block_prediction):
                        print(block_prediction)
                        block_prediction = ""
                        prev_font = (font_name, font_size)
                        continue
                    extracted_text.append({
                        'txt':filter_reference(block_prediction),
                        'font':font_name,
                        'size':font_size
                    })
                    block_prediction = span["text"]
                    prev_font = (font_name, font_size)
    return extracted_text

def cluster_text(raw_text:list, fonts:dict)->list:
    """Groups text blocks based on their font and size.

    Arguments:
        raw_text: A list of text blocks.
        fonts: A map of font names and their properties.

    Returns:
        clustered_text: A list of grouped text blocks.
    """
    clustered_text = []
    print(fonts)
    if len(raw_text)<=1:
        return raw_text
    clustered_text.append(raw_text[0])
    for rtext in raw_text[1:]:
        if rtext['size'] == clustered_text[-1]['size'] and\
              rtext['font'] == clustered_text[-1]['font']:
            clustered_text[-1]['txt'] += f" {rtext['txt']}"
        else:
            clustered_text.append(rtext)
    return clustered_text

def get_metadata(pdf_doc: utils.pymupdf.Document) -> dict[str,str]:  #pylint: disable=W0613
    """Get metadata of original PDF document.

    Arguments:
        pdf_doc: The original PDF document.

    Returns:
        metadata: The PDF document's metadata.
    """
    return {"title":None, "author":None}

def get_chapters(text_clustered:list)->list:
    """Get a list of text grouped by chapter.

    Arguments:
        text_clustered: A list of text blocks.

    Returns:
        text_ret: A list of text grouped by chapter.
    """
    text_ret = ' '.join([i['txt'] for i in text_clustered])
    return [text_ret]

def main():#pylint: disable=R0914
    in_file_path, out_file_path, language = input_tool.get_sys_input(os.path.dirname(__file__))
    PATTERN_HEADER = r"arXiv:2310\.03605v3  \[cs.CR\]  29 Nov 2023"  #pylint: disable=C0103
    PATTERN_FOOTER = r"pag. [0-9]+Phenomena Journal \| www\.phenomenajournal.itLuglio-Dicembre 2021 \| Volume 3 \|( Numero [0-9]+ \|)? Ipotesi e metodi di studio"  #pylint: disable=C0103,C0301
    pdf_doc = fitz.open(in_file_path)
    fonts = {}#get_fonts(pdf_doc)
    text = get_chapter_text(pdf_doc, PATTERN_HEADER, PATTERN_FOOTER)
    text = cluster_text(text, fonts)
    with open("test.json", "w", encoding="UTF-8") as outfile:
        outfile.write(json.dumps(text, separators=(",", ":"), indent=4))
    chapters = get_chapters(text)
    metadata = get_metadata(pdf_doc)
    chapter_titles = ["1"]
    chapters_paths = []
    m4b.init(BACK_END_TTS)
    with tempfile.TemporaryDirectory() as tempdir:
        for idx, ch in enumerate(chapters):
            filepath = os.path.join(tempdir, f"{idx}.txt")
            print(ch)
            if m4b.generate_audio(ch, filepath, lang=language, backend=BACK_END_TTS):
                chapters_paths.append(filepath)
    metadata_output = ffmetadata_generator.generate_ffmetadata(chapters_paths,
                                                chapter_titles=chapter_titles,
                                                title=metadata["title"],
                                                author=metadata["author"])
    m4b.generate_m4b(out_file_path, chapters, metadata_output)

if __name__ == "__main__":
    main()
