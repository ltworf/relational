Requirements:
1)Python 2.6;
2)PyQt for python 2.6 (it should already include the qt libs);
3)Py2exe
4)Innosetup

It might be necessary to have the: Microsoft Visual C++ 2008 Redistributable Package, because python 2.6 uses it and it's not installed by default in windows.


	Create an exe file
- Move the file windows/input.py to ../
- Chech that the version number is correct
- Execute "python input.py py2exe"

At the end, there should be a directory named "dist" containing the exe file and the needed libs (excluding for the c++ one)

	Create the setup with Inno Setup
- Move windows/ss.iss to ../
- Open ss.iss with Inno Setup, Build and Compile

A directory named "Output" will be created, which will contain the installer.

Notes:
- To create the setup, don't move the "dist" directory or its content.
- Do not delete or move the directory windows/font dejavu
