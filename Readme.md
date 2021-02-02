#  Readme
Based on latex-calgen by simu https://github.com/simu/latex-calgen

## Features:
1. Can include a customized background image and a common footer image.
2. Ability to load data from a .csv file

## Prerequisites:

The package requires a working installation of Latex. If not installed you can install it from here : 

https://ctan.math.illinois.edu/systems/win32/miktex/setup/windows-x64/basic-miktex-20.12-x64.exe

Please enable automatically install missing packages option when installing

## Inserting Images:

You can either include one title image per month or a different image every month. Please have the images in a folder and the image names must be in three letter month format with the first letter capitalized, i.e Jan, Feb, etc.. (Refer to the Images folder provided for more clarity). If only using a single picture for all months please name it 'Jan'. 

A footer image must be specified at all times and named 'Footer'. 

In the Images field of the app select the folder containing these images.

**Please make sure that there are no spaces in the folder name**

## Inserting Event Data:

For inserting event data, please include the data in a .csv file. 

Please utilize the provided TestInput.csv and change the entry names to suit your needs. The column header (which currently are written as Entry1, Entry2 etc ) specify the field name while the content of that column specify the information to be included with the field. 

**NOTE:  The first run might take a while to generate the pdf, this will be as it is installing LaTex dependencies. This is normal and expected behavior**
