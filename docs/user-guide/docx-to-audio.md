---
title: Word documents
description: Instructions on converting Word documents to MP3.
---

This page explains how to convert a Microsoft Word document to audio files.

!!! important
    The document's extension must be `.doc` or `.docx`.

## Run the script

To convert a Microsoft Word document to audio files:

1. Open a terminal window.
1. [Download the scripts][1].
1. [Install the required libraries][2].
1. Run the `docx2audio.py` script.

    ```console
    python3 docx2audio.py <PATH_TO_FILE>.docx <LANGUAGE>
    ```

    <dl>
      <dt><code>&lt;PATH_TO_FILE&gt;</code></dt>
      <dd>The full path to the Microsoft Word document that you want to convert to audio files.</dd>
      <dt><code>&lt;LANGUAGE&gt;</code></dt>
      <dd>The desired output language's [Internet Engineering Task Force (IETF) language tag][3]. For example, English's tag is `en`.</dd>
    </dl>

This saves audio files in the current folder.

## View the output

The script creates MP3 files and plain text files as it converts the Microsoft Word document. For large documents, it may create multiple MP3 files and text files.

For example, if the script creates X number of files:

* MP3 files have a name like `<ORIGINAL_FILE_NAME>.docx.cX.mp3`
* Text files have a name like `<ORIGINAL_FILE_NAME>.docx.cX.txt`

<dl>
  <dt><code>&lt;ORIGINAL_FILE_NAME&gt;</code></dt>
  <dd>The Microsoft Word document's original name.</dd>
</dl>

Look for the MP3 files in the current folder. They have the same name as the converted file, but with a `.mp3` extension.

![docx-to-audio-output](../img/docx-to-audio-output.png)

[1]: ./download-scripts.md#download-the-scripts
[2]: ./install-libraries.md#install-the-required-libraries
[3]: https://en.wikipedia.org/wiki/IETF_language_tag
