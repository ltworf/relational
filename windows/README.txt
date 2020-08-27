Due to py2exe and pyinstaller not working at all, the setup now just installs python
uses pip to install the requirements and then creates some links to start relational.

You will need:

1) Innosetup
2) The python installer executable in the windows directory

	Create the setup with Inno Setup
- Run make or it will just never work
- Move windows/ss.iss to ../
- Open ss.iss with Inno Setup, Build and Compile

A directory named "Output" will be created, which will contain the installer.
