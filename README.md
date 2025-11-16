# tspace
tspace is short for **t**erminal **space**. A terminal ui (tui) built with textual library and python 3.11 to check for how much space a directory occupies on the disk.
note: the app checks for **apparent-size** so it **does not reflect how much the directory takes up *disk space* but instead reflect how much the individual directory takes up real bytes** so it does **not** show how much it uses space but is shows *how big is it*. 

App does the same job as `du --apparent-size -sh <folder>`, but slower and with a TUI

