---
title: PowerPoint presentations
description: Instructions on converting PowerPoint presentations to M4b.
---

This page explains how to convert a Microsoft PowerPoint presentations to an audio file.

!!! important
    The presentation's extension must be `.pptx`.

## Run the script

To convert a Microsoft PowerPoint presentation to an audio file:

1. Open a terminal window.
1. [Download the scripts][1].
1. [Install the required libraries][2].
1. Run the `pptx2audio.py` script.

    ```console
    python3 pptx2audio.py <PATH_TO_FILE>.pptx <LANGUAGE>
    ```

    <dl>
      <dt><code>&lt;PATH_TO_FILE&gt;</code></dt>
      <dd>The full path to the text file that you want to convert to an audio file.</dd>
      <dt><code>&lt;LANGUAGE&gt;</code></dt>
      <dd>The desired output language's [Internet Engineering Task Force (IETF) language tag][3]. For example, English's tag is `en`.</dd>
    </dl>

This saves an audio file in the current folder.

## View the output

Look for the audio file in your current folder. It has the same name as the converted file, but with a `.m4b` extension.

![successful-conversion](../img/pptx-to-audio-output.png)

[1]: ./download-scripts.md#download-the-scripts
[2]: ./install-libraries.md#install-the-required-libraries
[3]: https://en.wikipedia.org/wiki/IETF_language_tag
