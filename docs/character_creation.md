# Scenario creation

This page describes of to define a character.

## Table of content

  * [Where](#Where)
  * [Prompt](#prompt)

## Where

A character is key/value pair that is defined in any yaml files inside the `prompts/characters` folder of the database.

## Prompt

Creating a character is very simple:
- the key is the name of the character
- the value can either be a string or a list of two string
  - if a string, that's the prompt of the character
  - if a list of two strings, the first one is the prompt of the character, the second one is added to the negative prompt

Examples:
```yaml
# Basic
alan_garner: Hangover, <lora:Hangover:0.8>

# Multiline
laura_prepon: >-
  laura prepon,
  <lora:laura prepon v1.35:1>

# With negative prompt
avril_lavigne:
  - woman, 4vr1ll4v1gn3 # character prompt
  - microphone # negative prompt
```
