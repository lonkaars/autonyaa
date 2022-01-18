#!/bin/python3
import urllib, sys, re, requests, xml.etree.ElementTree as et, transmission_rpc, os, json

current_path = os.path.dirname(__file__)
config_file = open(current_path + "/configuration.an", "r")
transmission_rpc_file = open(current_path + "/transmission.json", "r")
transmission_rpc_config = json.loads(transmission_rpc_file.read())

transmission_client = transmission_rpc.Client(host='localhost', port=9091,)

def generate_url(query):
  return "https://nyaa.si/?" + urllib.parse.urlencode({"q": query, "page": "rss"})

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
    if match == None or match.start() != 0 or match.end() != len(name):
      return [ False, {} ]
    vars = {}
    for index, name in enumerate(variables):
      vars[name] = match.groups()[index]
    return [ True, vars ]
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

def parse_config_section(section):
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
  return props

def parse_config_file():
  parsed_sections = []
  contents = config_file.read()
  sections = [x.strip() for x in contents.split("\n\n")]
  while "" in sections:
    sections.remove("")

  for section in sections:
    parsed_sections.append(parse_config_section(section))

  return parsed_sections

def start_dl(result, section):
  print(result, section)

def main():
  sections = parse_config_file()
  for section in sections:
    response = requests.get(generate_url(section["name"])).text
    root = et.fromstring(response)
    results = [child for child in root[0] if child.tag == "item"]
    for result in results:
      match = section["match-name"]([el.text for el in result if el.tag == "title"][0])
      if match[0]: start_dl(result, match[1])

if __name__ == "__main__":
  main()

