Requirements:
1)Python 3.4, 32bit
2)PyQt5 for python 3.4, 32bit (it should already include the qt libs);
3)Py2exe
4)Innosetup

It is necessary to have the: Microsoft Visual C++ 2010 Redistributable Package.

	Create an exe file
- Move the file windows/input.py to ../
- Chech that the version number is correct
- Execute "python input.py py2exe"

At the end, there should be a directory named "dist" containing the exe file and the needed libs (excluding for the c++ one)
within the dist directory there should be a "platforms" directory with a dll the PyQt5 directory.

	Create the setup with Inno Setup
- Move windows/ss.iss to ../
- Download the Microsoft Visual C++ 2010 Redistributable, call it vcredist_x86.exe and save it in the relational main directory
- Open ss.iss with Inno Setup, Build and Compile

A directory named "Output" will be created, which will contain the installer.

Notes:
- To create the setup, don't move the "dist" directory or its content.
- Do not delete or move the directory windows/font dejavu
- If the shell is open, it will not work. The windows shell does not support unicode and will generate exceptions when trying to print expressions on it
