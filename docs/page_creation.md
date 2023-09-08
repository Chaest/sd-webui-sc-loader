# Page creation

This page describes of to define a "page".

## Table of content

  * [Where](#Where)
  * [Main structure](#main-structure)
  * [Characters](#characters)
  * [Panels](#panels)
  * [Scenarios](#scenarios)
  * [Texts](#texts)

## Where

A page is a yaml key/value that can be added in any yaml within the `pages` folder inside the database.

## Main structure

A page is defined as a list of character types, a panel layout, a list of scenarios, and a a list of texts. Hence the main structure of the yaml should be:

```yaml
<name of the scenario>:
    characters: <list of character types>

    panels: <panel layout>

    scenarios: <list of scenarios>

    texts: <list of texts>
```

## Characters

The `characters` key only contain a list of string the corresponds to some of the character types defined in the database.

There should be all the characters required by the scenarios used in the scenario list.

Example:

```yaml
page_name:
  characters:
    - character1
    - character2

  ...
```

## Panels

The panel layout is a list of 3 string containing letters that describe panel.
Currently, four letters are supported:
 - **L**: landscape, takes up a full line
 - **C**: case, takes up half a line
 - **P**: portrait: takes up a third of a line
 - **l**: small landscape, takes up two third of a line

A line is basically 1024x512, images will resized to fit there place, so used scenarios that match their panels. Upscaling will be taken into account.

Here are a few examples of layout:
```yaml
# three scenarios, one per line
page_name:
  panels:
    - L
    - L
    - L

# six scenarios, 2 on the first line, 3 on the second and 1 on the last
page_name:
  panels:
    - CC
    - PPP
    - L

# fix scenarios, 2 on the first and last line, 1 on the second
page_name:
  panels:
    - CC
    - L
    - lP
```

## Scenarios

A list of scenario names. Should match the number of expected scenarios define in the layout.

## Texts

A list of texts. Each will be added at the bottom of the corresponding panel Should match the number of expected scenarios define in the layout.
