'''
This script must be kept in a folder where the zip file to be validated is present.
No other files/folders must be present in the working location.
'''

import zipfile, os

# Zip file location
file_to_be_validated = '21f2000620.zip' # Replace the name with the zip file name
status = "Failed"

try:
  with zipfile.ZipFile(file_to_be_validated, 'r') as zip_ref:

      # extract the contents in the current directory
      zip_ref.extractall("Unzipped")
      print('Unzipped successfully')

      # validating the presence of project folder
      f = 0
      if len(os.listdir("./Unzipped")) == 1 and os.path.isdir("./Unzipped"):
          print("Project folder found in the root directory of the submission")
          dir_to_flatten = os.listdir("./Unzipped/")[0]
          for dirpath, dirnames, filenames in os.walk("./Unzipped/" + dir_to_flatten):
              if "lib" not in dirpath and "Lib" not in dirpath:
                  for filename in filenames:
                      if filename.endswith(".py"):
                          print("Python file found")
                          status = "Passed"
                          f = 1
                          break

          if f == 0:
              print("No Python file found")

      else:
          print("Project folder not found in the root directory of the submission")

except:
  print('Unable to extract the file')
finally:
  print("Validation Status:", status)