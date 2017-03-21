
cd relational_gui
pyuic5 -o maingui.py maingui.ui
pyuic5 -o survey.py survey.ui
pyuic5 -o rel_edit.py rel_edit.ui

cd ..
python relational_gui.py
