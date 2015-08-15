# Pyrite
Pyrite is a bare-bones Python text editor that keeps things
minimal, yet still maintains a rich-looking design, which
is fully customizable. 

## Features
- Syntax highlighting
- Manual code-completion
- Toggle-able line numbering
- Customization of coloring via settings file
- Common text editor features

## Customizing the Colors
To change the colors, open the settings.xml file.
This file is easily-understandable XML. To set the color
value for a given item simply edit the value between the
angled brackets that correspond to that item. All color
values should be in 6-digit hexadecimal format like so:
<br />
**Pure Red:** *\#FF0000* <br />
**Pure Green:** *\#00FF00* <br />
**Pure Blue:** *\#0000FF* <br />

### Example
Here's an example demonstrating changing the color for
a line comment to pure red. Simple find the following block
in the **settings.xml** file and change the value for the color tag
```xml
<style type="python">
        <item>Comment</item>
        <side>Fore</side>
        <color>#626C67</color>
</style>
```
