---
title: Ebooks
description: Instructions on converting Ebooks to MP3.
---

This page explains how to convert an ebook to audio files.

!!! important
    The file's extension must be `.epub`.

## Run the script

To convert an ebook to audio files:

1. Open a terminal window.
1. [Download the scripts][1].
1. [Install the required libraries][2].
1. Run the `ebook2audio.py` script.

    ```console
    python3 ebook2audio.py <PATH_TO_FILE>.epub <LANGUAGE>
    ```

    <dl>
      <dt><code>&lt;PATH_TO_FILE&gt;</code></dt>
      <dd>The full path to the text file that you want to convert to an audio file.</dd>
      <dt><code>&lt;LANGUAGE&gt;</code></dt>
      <dd>The desired output language's [Internet Engineering Task Force (IETF) language tag][3]. For example, English's tag is `en`.</dd>
    </dl>

This saves audio files in the current folder.

## View the output

The script creates MP3 files and plain text files as it converts the ebook. For large ebooks, it may create multiple MP3 files and text files.

For example, if the script creates X files:

- MP3 will have a name like `itemX.mp3`.
- Text  will have a name like `itemX.log`

Look for the MP3 files in the current folder.

![ebook-to-audio-output](../img/ebook-to-audio-output.png)

[1]: ./download-scripts.md#download-the-scripts
[2]: ./install-libraries.md#install-the-required-libraries
[3]: https://en.wikipedia.org/wiki/IETF_language_tag
