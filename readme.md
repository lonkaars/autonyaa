# autonyaa

script that automatically adds new anime episodes from nyaa.si to a
transmission daemon, and symlinks them once they're done downloading

it's intentionally janky, because i don't expect it to work for a long time. if
it keeps working (well) for long enough i'll refactor/document the code better.

## configuration

autonyaa is configured through two files: configuration.an and
transmission.json. both have to be located in the same folder as the python
script itself. example config files are included.

transmission.json is a regular json file containing credentials for connecting
to the transmission daemon. note that if you've configured a localhost
whitelist for your transmission-daemon, that the `username` and `password` keys
can be either set to `null` or be omitted entirely.

configuration.an is a file with a custom key-value syntax for defining how
autonyaa should look up and match torrent titles. if you want to keep track of
multiple anime's, you can define multiple config sections by seperating them
with an empty line. here's a reference for all the configuration keys:

### name

```
name <string>
```

set the name and search query

### filename

```
filename <string>
```

set the filename for finished downloads. finished downloads are hard-linked
into [destination](#destination), with any variables replaced with values from
regex groups. for more info on variables, see [match-name](#match-name).

example:

```
filename Anime-name_s01e${e}.${x}
```

### match-name

```
match-name <regex> <groups>
```

filter torrent titles using regex. for a match to be successful, the entire
regex has to match. match groups are mapped onto the variable names defined
after the regex, and can be reused for the target filename.

example

```
match-name /\[coolgroup\] Anime name episode (\d{2}) - episode title \(1080p\)\.(.+)/ e x
```

> in this example, the variable e is set to the first group (`(\d{2})`), and x
> is set to (`(.+)`). for regex help, see [regexr](https://regexr.com)

### match-submitter

```
match-submitter <string>
```

filter torrent submitter using name.

example

```
match-name coolgroup
```

### destination

```
destination <folder>
```

destination folder

## todo

- [ ] implement episode limit
- [x] implement match-submitter


