.. link: 
.. description: 
.. tags: 
.. date: 2014/01/01 10:54:05
.. title: Tutorial
.. slug: tutorial


Introduction
============
Relational is an educational software. The purpose is to show if the query is correct or not. It doesn't replace and will never be able to replace the knowledge of relational algebra. It is just a tool to check the queries, which can make life easier.
Do not expect it to replace your brain please.

Create your own relation
========================

Before starting, we will create an example relation, that we will use in this tutorial.

Relations are stored into text files. One relation into one file.
By default relations will have .csv extension.

If you aren't interested in creating a new relation because you want to use the examples shipped with the installation, you can skip this.

Click on the "New relation" button.

Now, on the 1st row add the names of the columns you want for your relation, you can add more columns clicking on "Add column".

Now populate the table with the values.

When you are done click "Ok", you will be prompted to insert the name for the new relation. Just use letters, if the name you insert is not valid, the relation will be deleted and an error will be shown.

Load a relation
===============
To load a relation from disk, press the Load relation button.
A file chooser dialog will be shown and you will need to select the file you want to open.
Once you've selected the file, you will be required to give a name to the relation. This name will be used in the queries. Relational will automatically suggest to name the relation like the file, but the name can be changed.

Repeat the operation until you've opened all the relations you're interested in.

Show a relation
===============
Once a relation is opened, you will be able to display it in the center table.
To show a relation, double click on it, in the list within the Relations frame.

You might be interested to show the fields of a relation, without showing it (because you want another relation in the center). To show the fields, single click on a relation in the Relations frame, and the fields will be listed in the Attributes frame.


1st query
=========
The query must be inserted into the large text box at the bottom of the window.
Try writing the name of one of the loaded relations and press Enter. This simple query will result a relation identical to the one requested.

Other queries
=============
By default the resulting query will be named _last1, but it is possible to override that writing a name for the resulting query in the small textbox in the left-bottom part of the window.

Since most of the symbols aren't present on keyboards, they are provided as buttons on the left part of the screen. Pressing one of those buttons will insert the corresponding symbol at the cursor's position in the query's textbox.

Save a relation
===============
A new relation created by a query or by editing a relation inserting and removing tuples can be saved pressing on the Save relation button. It will save the currently selected relation.
A dialog will ask where to save the file.

