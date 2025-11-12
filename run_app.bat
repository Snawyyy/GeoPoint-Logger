@echo off
echo Running the application...
cd /d "C:\Users\eitan_k\projects\Tree_Log"
py -X faulthandler -c "import sys; sys.path.insert(0, 'src'); from src.main import main; main()"