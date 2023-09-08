
Windows Installer for MrPython
==============================

To (re)build the windows installer, you need :

 - windows (10, for now) installed on the computer
 
 - PyInstaller, cf. https://www.pyinstaller.org/
 (obviously Python also, cf. https://www.python.org/)
 
 - Inno Setup, cf. https://jrsoftware.org/isinfo.php
 
 
The build steps are as follows, from a copy of the
 `win-installer` branch of MrPython repository :
 
 - first, open a PowerShell window, and go to
 the `mrpython\` subdirectory of the projet.

 - second, build the pyinstaller app folder with
 the following command:

```
PS..MrPython\mrpython> pyinstaller.exe .\MrPython_win.spec
...
```
(answer `Y`es to the possible questions, especially when rebuilding)
 
If all goes well, the app folder will be built into
the `dist\MrPython` folder. You can try the executable which
is `dist\MrPython\Application.exe`

 - third, we create the installer executable, and for
 this we go back to the main repository folder, we launch
 the **InnoSetup compiler** and load the file: `win_installer_script.iss`.
 Within InnoSetup we just need to select `Compile` in the `Build` menu
 (or type `Ctrl-F9`).  This should generate the file
 `mrpython_M_m_x_install_LANG.exe` in the `Output\` directory.
 with `M` the major version number, `m` minor, `x` extra
 version infos and `LANG` the default language support (multilingual
  support will be activated at some point).
  
And that's all folks
