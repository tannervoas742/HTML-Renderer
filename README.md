# HTML-Renderer
Uses Yattag to generate HTML webpage from content contained in JSON files.

# Dictionary Key Command List:
- ```#CLASS(T1 T2 T3....)```: Used to set the items class (this controls how styles are applied and you will occasionally need this if you want to beautify your code webpages).
  - Classes are inherited by all children objects and can have any number of them.
  - Each time a ```#CLASS``` call is seen it totally overwrites the existing classes.
  - If you want to just add a class or remove a class can use ```#ADD_CLASS(T1 T2 T3....)``` or ```#REMOVE_CLASS(T1 T2 T3....)``` instead
  - ```T1 T2 T3``` in all above examples have no special meaning. Just using an example where add 3 classes. Any number of classes can be given with any name.
- ```#HIDDEN```: Hides this item and all of its sub-content. Just used for compute.
- ```#H0```, ```#H1```, ```#H2```, ```#H3```: Determines text size for a given header.
- ```#P0```, ```#P1```, ```#P2```, ```#P3```: Determines text size for a given header and all its children.
  - If H and P are used in same command H is used on Header but P value is used on children.
- ```#HR_BEFORE```, ```#HR_MIDDLE```, ```#HR_AFTER```: Adds line breaks at designated location
- ```#TABLE```: Takes either a dictionary or a list and displays it as a table. No nesting allowed.
- ```#LOOKUP_TABLE(START, STOP)```: Takes a list of column names and fills in rows using previous computed values.
  - Indexing starts from 1 and goes to (inclusive) up to STOP
  - Previously computed values but have already been handled. i.e if use a lookup table with precedence 10 and one of the rows has precedence 12 (or no precedence) then you will get an error. #HIDDEN items are an exception and get computed immediately even if no precedence is given.
  - Previously computed values can be shorter than STOP. In this case last value just repeats.
- ```#CONCAT_LINES```: Expects a list and will join them on line breaks when displayed.
- ```#APPEND_AFTER(VAL)```, ```#APPEND_BEFORE(VAL)```: Only available on ```#INC``` and ```#RANGE``` statements at the moment. Appends the VAL to the computed list either before or after.
- ```#LOOKUP(KEY)```: Only valid on ```#INC``` and ```#RANGE``` at this moment. Replace the calculated value with a value from a already defined table.
  - e.g. ```"_st#HIDDEN": {"1": "1st", "2": "2nd"}``` is an example of a table that can be defined earlier. For convenience these can be defined at a high level and they persist until replaced.
- ```CALL(FUNC)```: Functions similar to lookup except FUNC should be a set of code that takes 1 argument (ARG) which is the value this key pairs with and replaces this value with said functions return value.

# In Text Command List:
- ```<LIST_START>```, ```<LIST_ITEM>```, ```<LIST_STOP>```: USeful in conjunction with ```CONCAT_LINES``` to make bulleted list.
- ```<GOTO:Text:File+Location>```: Adds a link to the given File (or external webpage) with the given Text. Optionally include +Location to designate jump to location in said file.
- ```<GOTO:File+Location>```: Adds a link to the given File (or external webpage). Optionally include +Location to designate jump to location in said file. If Location is used Text = Location, else Text = File
- ```<BOLD>```: Make text bold until ```</BOLD>``` is encountered
- ```<ITALIC>```: Make text italic until ```</ITALIC>``` is encountered 
- ```<HIGHLIGHT>```: Highlight text until ```</HIGHLIGHT>``` is encountered
- ```<SMALL>```: Make text smaller until ```</SMALL>``` is encountered
- ```<STRIKE>```: strikethrough text until ```</STRIKE>``` is encountered
- ```<UNDER>```: underline text until ```</UNDER>``` is encountered
- ```<SUB>```: Make text into a subscript until ```</SUB>``` is encountered
- ```<SUP>```: Make text into a superscript until ```</SUP>``` is encountered