#!/usr/bin/python3
"""
[`docx2audio.py`](https://github.com/deangelisdf/write2audiobook/blob/main/docx2audio.py)

Convert a `.doc` or `.docx` file to MP3 files.

Usage example:
    `python docx2audio.py document.docx en`
"""

import os
import logging
from typing import Union, Generator
from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table, _Row
from docx.text.paragraph import Paragraph
from backend_audio import ffmetadata_generator
from backend_audio import m4b
from frontend import input_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACK_END_TTS = m4b.get_back_end_tts()
LANGUAGE = "it"

TITLE_KEYWORD  = {"it-IT":"TITOLO",   "en":"TITLE"}
CHAPTER_KEYWORD= {"it-IT":"CAPITOLO", "en":"CHAPTER"}
TITLE_TOKENS   = ('Heading 1', 'Title', 'Titolo')
LIST_ITEM_TOKEN= 'List Paragraph'
CHAPTER_TOKEN  = 'Heading 2'

def __get_parent_element(parent: Union[Document, _Cell, _Row]):
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc #pylint: disable=W0212
    elif isinstance(parent, _Row):
        parent_elm = parent._tr #pylint: disable=W0212
    else:
        raise ValueError("something's not right")
    return parent_elm

def iter_block_items(
    parent:Union[Document, _Cell, _Row]
) -> Generator[Union[Paragraph, Table], None, None]:
    """
    Create a reference to each paragraph and table within a section
    in document order. Each returned value is either a Table or Paragraph object.
    The `parent` object can be a Cell, Paragraph, or Table object.

    Arguments:
        parent: The main document object or an individual `Cell` object.

    Yields:
        A Paragraph or Table object.
    """
    parent_elm = __get_parent_element(parent)
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def extract_chapters(doc:Document,
                     style_start_chapter_name:tuple[str] = TITLE_TOKENS
                     ) -> list[Union[Paragraph, Table]]:
    """Get chapters as a list of paragraphs and tables. The chapters comprise a
    title (with Word styles like Heading1 or Title) and the corpus (with other Word styles).

    Arguments:
        doc: The main Word document item.
        style_start_chapter_name: Identifiers for titles in the Word document.

    Returns:
        result: A list of Paragraph or Table objects.
    """
    temp_chapters: list[list[Union[Paragraph, Table]]] = []
    temp:list[Union[Paragraph, Table]] = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            if block.style.name in style_start_chapter_name:
                if len(temp) > 1:
                    temp_chapters.append(temp)
                temp = []
            if len(block.text) == 0:
                continue
        temp.append(block)
    return [i for i in temp_chapters if len(i)>0]

def get_text_from_paragraph(block: Paragraph, language:str,
                            idx_list:int) -> tuple[str, int]:
    """Get text from a Paragraph object.

    Arguments:
        block: The Paragraph object to get text from.
        language: The language of the Paragraph object's content.
        idx_list: The current count of Paragraph objects.
    Return:
        text: The Paragraph object's content.
        idx_list: The Paragraph's location in the original document.
    """
    text = ""
    if block.style.name == LIST_ITEM_TOKEN:
        text += f"\t{idx_list}: {block.text}.\n"
        idx_list += 1
        return text, idx_list
    idx_list = 0
    if block.style.name == CHAPTER_TOKEN:
        text += f"\n.\n{CHAPTER_KEYWORD[language]}: "
    text += f"{block.text}\n"
    return text, idx_list

def get_text_from_table(block: Table, language:str) -> str: #pylint: disable=W0613
    """Get text from a Table object.

    Arguments:
        block: The Table object to get text from.
        language: The language of the Table object's content.
    Return:
        text: The Table object's content
    """
    text = ""
    for row in block.rows:
        row_data = []
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                row_data.append(paragraph.text)
        text += "{}\n".format('\t'.join(row_data))
    return text

def get_text_from_chapter(chapter_doc:list[Union[Paragraph, Table]],
                          language:str=LANGUAGE) -> tuple[str, str]:
    """Get text from a chapter in the original document.

    Arguments:
        chapter_doc: A list of Paragraph and Table objects.
        language: The language of the chapter's content.

    Returns:
        result: A tuple of the object's title and its text content.
    """
    title_str = chapter_doc[0].text
    text = f"{TITLE_KEYWORD[language]}: {title_str}.\n"
    idx_list = 0
    for block in chapter_doc[1:]:
        if isinstance(block, Paragraph):
            temp_text, idx_list = get_text_from_paragraph(block, language, idx_list)
            text += temp_text
        elif isinstance(block, Table):
            text += get_text_from_table(block, language)
    return text, title_str

def main():
    in_file_path, out_file_path, language = input_tool.get_sys_input(os.path.dirname(__file__))
    chapters = []
    chapters_path: list[str] = []
    title_list:list[str] = []

    m4b.init(BACK_END_TTS)

    document = Document(in_file_path)
    chapters = extract_chapters(document)
    for idref, chapter in enumerate(chapters):
        output_mp3_path   = f"{in_file_path}.c{idref}.mp3"
        text_chapther, title = get_text_from_chapter(chapter)
        title_list.append(title)
        logger.info("idref %s", idref)
        with open(f"{in_file_path}.c{idref}.txt", "w", encoding="UTF-16") as out_debug_file:
            out_debug_file.write(text_chapther)
        if m4b.generate_audio(text_chapther, output_mp3_path,
                              lang=language, backend=BACK_END_TTS):
            chapters_path.append(output_mp3_path)
    metadata_output = ffmetadata_generator.generate_ffmetadata(chapters_path,
                                                               chapter_titles=title_list)
    m4b.generate_m4b(out_file_path, chapters_path, metadata_output)
    m4b.close_edge_tts()

if __name__ == "__main__":
    main()

__author__ = "de angelis domenico francesco"
