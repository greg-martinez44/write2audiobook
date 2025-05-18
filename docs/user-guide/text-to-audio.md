---
title: Text files
description: Instructions on converting plain text files to MP3.
---

This page explains how to convert plain text files to audio files.

!!! important
    * The text file's encoding must be **UTF-8**.
    * The text file's extension must be `.txt`.

## Run the script

To convert a text file to an audio file:

1. Open a terminal window.
1. [Download the scripts][1].
1. [Install the required libraries][2].
1. Run the `txt2audio.py` script.

    ```console
    python3 txt2audio.py <PATH_TO_FILE>.txt <LANGUAGE>
    ```

    <dl>
      <dt><code>&lt;PATH_TO_FILE&gt;</code></dt>
      <dd>The full path to the text file that you want to convert to an audio file.</dd>
      <dt><code>&lt;LANGUAGE&gt;</code></dt>
      <dd>The desired output language's [Internet Engineering Task Force (IETF) language tag][3]. For example, English's tag is `en`.</dd>
    </dl>

This saves an audio file in the current folder.

## View the output

Look for the MP3 file in the current folder. It has the same name as the converted file, but with a `.mp3` extension.

![successful-conversion](../img/example-output.png)

[1]: ./download-scripts.md#download-the-scripts
[2]: ./install-libraries.md#install-the-required-libraries
[3]: https://en.wikipedia.org/wiki/IETF_language_tag
