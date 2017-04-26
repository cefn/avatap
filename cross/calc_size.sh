# Calculates the total file size in bytes of all .py files in the folder
stat -c '%s' `find . -name '*.py'` | paste -sd+ | bc
