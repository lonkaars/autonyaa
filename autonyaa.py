#!/bin/python3
import urllib
import sys
import re

def generate_url(query):
  return "https://nyaa.si/?" + urllib.urlencode({"q": query})

def fill_format_string(format_string, variables):
  return_string = format_string
  for var in variables.items():
    return_string = return_string.replace("${" + var[0] + "}", var[1])
  return return_string

def parse_config_prop_name(line):
  return line[5:].strip()

def parse_config_prop_filename(line):
  def return_funtion(variables):
    return fill_format_string(line[9:].strip(), variables)
  return return_funtion

def parse_config_prop_match_submitter(line):
  return line[16:].strip()

def parse_config_prop_match_name(line):
  parser = re.compile(r'(\/.+\/) (.+)')
  content = line[11:].strip()
  match = parser.match(content).groups()

  parser = re.compile(match[0][1:-1])
  variables = [x.strip() for x in match[1].split(" ")]
  def return_funtion(name):
    match = parser.match(name)
    fits = match.start() == 0 and match.end() == len(name)
    vars = {}
    for index, name in enumerate(variables):
      vars[name] = match.groups()[index]
    return [ fits, vars ]
  return return_funtion

def parse_config_prop_destination(line):
  return line[12:].strip()

def parse_config_prop_episodes(line):
  return int(line[9:].strip())

config_props = [
  {"prop": "name",            "parser": parse_config_prop_name},
  {"prop": "filename",        "parser": parse_config_prop_filename},
  {"prop": "match-submitter", "parser": parse_config_prop_match_submitter},
  {"prop": "match-name",      "parser": parse_config_prop_match_name},
  {"prop": "destination",     "parser": parse_config_prop_destination},
  {"prop": "episodes",        "parser": parse_config_prop_episodes},
]

def parse_config_section(section, index):
  props = {
    "name": "",
    "filename": None,
    "match-submitter": [],
    "match-name": None,
    "destination": "",
    "episodes": 0,
  }
  lines = section.split("\n")
  for line in lines:
    for p in config_props:
      if line.startswith(p["prop"] + " "):
        props[p["prop"]] = p["parser"](line)
  print(props)
  print(props["match-name"]("[SubsPlease] Sabikui Bisco - 01 (1080p) [8F2D5ABB].mkv"))
  print(props["filename"]({"e": "01", "x": "mkv"}))

def parse_config_file(location):
  parsed_sections = []

  with open(location, 'r') as file:
    contents = file.read()
    sections = [x.strip() for x in contents.split("\n\n")]
    while "" in sections:
      sections.remove("")

    for index, section in enumerate(sections):
      parsed_sections.append(parse_config_section(section, index))

  return parsed_sections

def main():
  config_file = sys.argv[1]
  if not config_file:
    print("usage: ./autonyaa.py [config_file]")
    exit(1)
  parse_config_file(config_file)

if __name__ == "__main__":
  main()

