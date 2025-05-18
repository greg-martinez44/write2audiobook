#!/usr/bin/python3
"""
[`ebook2audio.py`](https://github.com/deangelisdf/write2audiobook/blob/main/ebook2audio.py)

dConvert a `.epub` file to MP3 files.

Usage example:
    `python ebook2audio.py book.epub en`
"""

import zipfile
import tempfile
import os
import logging
import codecs
from lxml   import etree
from backend_audio import m4b
from backend_audio import ffmetadata_generator
from frontend import input_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACK_END_TTS = m4b.get_back_end_tts()
SKIP_IDREF = ["coverpage",
              "frontespizio",
              "footnotes",
              "copyright"]

def extract_by_epub(epub_path: str, directory_to_extract_path: str) -> None:
    """Unzip the `epub` file to a temporary folder.

    Arguments:
        epub_path: The path to the `epub` file.
        directory_to_extract_path: The temporary folder to unzip `epub` file to.
    """
    logger.debug("Extracting input to temp directory %s.", directory_to_extract_path)
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_path)

def get_guide_epub(root_tree: etree.ElementBase) -> dict[str, str]:
    """Get the guide information from the `content.opf` file.

    Arguments:
        root_tree: The XML tree's base from the `epub` file's content.

    Returns:
        guide_res: A map of the guide XML node types and their hyperlink content.
    """
    guide_res = {}
    for reference in root_tree.xpath("//*[local-name()='package']"
                                "/*[local-name()='guide']"
                                "/*[local-name()='reference']"):
        guide_res[reference.attrib['type']] = reference.attrib['href']
    return guide_res

def prepocess_text(text_in: str) -> str:
    """Remove non-audible characters.

    Arguments:
        text_in: The raw `epub` file's content.

    Returns:
        text_out: The processed `epub` file's content.
    """
    text_out = codecs.decode(bytes(text_in, encoding="utf-8"), encoding="utf-8")
    text_out = text_out.replace('\xa0', '')
    text_out = text_out.replace('\r\n\t', '')
    text_out = text_out.replace('\r\n', '\n')
    return text_out.strip()

def get_text_from_chapter(root_tree: etree._ElementTree,
                          idref_ch : str, content_dir_path: str,
                          guide_manifest: dict[str,str]) -> tuple[str, dict[str,str]]:
    """Use the `content.opf` XML tree to read and parse a chapter's HTML path.

    Arguments:
        root_tree: The XML tree's base from the `epub` file's content.
        idref_ch: The chapter's XML ID.
        content_dir_path: The path to the XML file.
        guide_manifest: A map of the guide XML node types and their hyperlink content.

    Returns:
        text_result: A tuple of the chapter's text and an empty dictionary.
    """
    text_result = ""
    for href in root_tree.xpath(f"//*[local-name()='package']"
                                f"/*[local-name()='manifest']"
                                f"/*[local-name()='item'][@id='{idref_ch}']"
                                f"/@href"):
        if href in guide_manifest.values():
            #Skip the chapter used as guide
            logging.debug("skipping %s", href)
            continue
        xhtml_file_path = os.path.join(content_dir_path, href)
        subtree = etree.parse(xhtml_file_path, etree.HTMLParser())
        for ptag in subtree.xpath("//html/body/*"):
            text_result += '\n'.join(text for text in ptag.itertext())
    return text_result, {}

def get_metadata(root_tree: etree._ElementTree) -> dict[str,str]:
    """Get basic metadata, like title, author and copyright information, from the `content.opf` file.

    Arguments:
        root_tree: The XML tree's base from the `epub` file's content.

    Returns:
        metadata_result: A map of node titles and their values from the XML tree's base.
    """
    metadata_leaf = root_tree.xpath("//*[local-name()='package']/*[local-name()='metadata']")[0]
    metadata_result = {"title":"", "author":""}
    namespace = metadata_leaf.nsmap
    if None in namespace.keys():
        del namespace[None]
    title  = metadata_leaf.xpath("//dc:title", namespaces=namespace)
    if len(title)>0:
        metadata_result["title"] = title[0].text
    author = metadata_leaf.xpath("//dc:creator", namespaces=namespace)
    if len(author)>0:
        metadata_result["author"] = author[0].text
    rights = metadata_leaf.xpath("//dc:rights", namespaces=namespace)
    if len(rights)>0:
        metadata_result["copyright"] = rights[0].text
    descr = metadata_leaf.xpath("//dc:description", namespaces=namespace)
    if len(rights)>0:
        metadata_result["description"] = descr[0].text
    return metadata_result

def extract_chapter_and_generate_mp3(tree: etree._ElementTree,  #pylint: disable=R0913,R0917
                                     output_file_path:str,
                                     mp3_temp_dir:str,
                                     content_file_dir_path:str,
                                     guide:dict[str,str],
                                     language:str) -> list[str]:
    """Get a chapter's ID reference and text from the `container.xml` file.

    Arguments:
        tree: The XML tree's base from the `epub` file's content.
        output_file_path: The path to save the MP3 file to.
        mp3_temp_dir: The temporary folder to save MP3 files to as the function parses the XML tree.
        content_file_dir_path: The path to the XML file.
        guide: A map of the guide XML node types and their hyperlink content.
        language: The content's language.

    Returns:
        chapters: A list of the saved MP3 file paths.
    """
    chapters = []
    for idref in tree.xpath("//*[local-name()='package']"
                            "/*[local-name()='spine']"
                            "/*[local-name()='itemref']"
                            "/@idref"):
        output_debug_path= os.path.join(os.path.dirname(output_file_path),
                                        f"{mp3_temp_dir}/{idref}.log")
        output_mp3_path  = os.path.join(os.path.dirname(output_file_path),
                                        f"{mp3_temp_dir}/{idref}.mp3")
        text_chapther, _ = get_text_from_chapter(tree, idref,
                                                content_file_dir_path,
                                                guide)
        logger.info("idref %s", idref)
        if any(idref.lower() in skippable for skippable in SKIP_IDREF):
            logger.debug("skip idref %s", idref)
            continue
        text_chapther = prepocess_text(text_chapther)
        with open(output_debug_path, "w", encoding="UTF-16") as out_debug_file:
            out_debug_file.write(text_chapther)
        if m4b.generate_audio(text_chapther, output_mp3_path,
                              lang=language, backend=BACK_END_TTS):
            chapters.append(output_mp3_path)
    return chapters

def main():
    tool_path: str = os.path.dirname(__file__)
    in_file_path, out_file_path, language = input_tool.get_sys_input(tool_path)
    chapters: list[str] = []

    m4b.init(BACK_END_TTS)
    with tempfile.TemporaryDirectory() as tmp_dir:
        extract_by_epub(in_file_path, tmp_dir)
        logger.info("Parsing 'container.xml' file.")
        container_file_path=os.path.join(tmp_dir, "META-INF/container.xml")
        tree = etree.parse(container_file_path)
        for root_file_path in tree.xpath( "//*[local-name()='container']"
                                        "/*[local-name()='rootfiles']"
                                        "/*[local-name()='rootfile']"
                                        "/@full-path"):
            logger.info("Parsing '%s' file.", root_file_path)
            content_file_path = os.path.join(tmp_dir, root_file_path)
            content_file_dir_path = os.path.dirname(content_file_path)
            tree = etree.parse(content_file_path)
            guide = get_guide_epub(tree)
            metadata_book_output = get_metadata(tree)
            logger.info("Parsed '%s' file.", root_file_path)
            with tempfile.TemporaryDirectory() as mp3_temp_dir:
                chapters += extract_chapter_and_generate_mp3(tree,
                                                             out_file_path,
                                                             mp3_temp_dir,
                                                             content_file_dir_path,
                                                             guide,
                                                             language)
                metadata_output = ffmetadata_generator.generate_ffmetadata(chapters,
                                                            title=metadata_book_output["title"],
                                                            author=metadata_book_output["author"])
                m4b.generate_m4b(out_file_path, chapters, metadata_output)

if __name__ == "__main__":
    main()

__author__ = "de angelis domenico francesco"
