#!/bin/python3
import urllib,\
       sys,\
       re,\
       requests,\
       xml.etree.ElementTree as et,\
       transmission_rpc,\
       os,\
       json

current_path = os.path.dirname(__file__)
config_file = open(current_path + "/configuration.an", "r")
transmission_rpc_file = open(current_path + "/transmission.json", "r")
transmission_rpc_config = json.loads(transmission_rpc_file.read())

transmission_client = transmission_rpc.Client(**transmission_rpc_config)
torrents = transmission_client.get_torrents()

def generate_url(section):
  options = { "q": section["name"], "page": "rss" }
  if section.get("match-submitter"): options["u"] = section["match-submitter"]
  return "https://nyaa.si/?" + urllib.parse.urlencode(options)

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
  parsed = line[9:].strip().split(" ")
  return { "var": parsed[0], "count": int(parsed[1]) }

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
    "episodes": {"var": None, "count": 0},
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

def episode_limit_reached(section, vars):
  return int(vars[section["episodes"]["var"]]) > section["episodes"]["count"]

def start_dl(result, section, vars):
  hash = result.findtext("nyaa:infoHash", None, {"nyaa": "https://nyaa.si/xmlns/nyaa"})
  torrent = [t for t in torrents if t.hashString == hash]
  if len(torrent) == 1:
    torrent = torrent[0]
    source = torrent.download_dir + "/" + torrent.files()[0].name
    target = section["destination"] + "/" + section["filename"](vars)
    if torrent.progress == 100 and not os.path.exists(target):
      print("linking " + section["name"])
      print(source + " -> " + target)
      os.makedirs(os.path.dirname(target), exist_ok=True)
      os.link(source, target)
  else:
    transmission_client.add_torrent(result.findtext("link"))
    print("adding torrent: " + result.findtext("title"))

def main():
  sections = parse_config_file()
  for section in sections:
    response = requests.get(generate_url(section)).text
    root = et.fromstring(response)
    results = root[0].findall("item")
    for result in results:
      match = section["match-name"](result.findtext("title"))
      if not match[0]: continue
      if episode_limit_reached(section, match[1]): continue
      start_dl(result, section, match[1])

if __name__ == "__main__":
  main()

