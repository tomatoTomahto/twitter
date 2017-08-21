import json

class FileWriter():
  def __init__(self, filename):
    self._filename = filename
  
  def write(self, message):
     with open(self._filename, 'a') as outfile:
        outfile.write(message + '\n')