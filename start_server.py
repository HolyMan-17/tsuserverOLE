#!/usr/bin/env python3

# tsuserver3, an Attorney Online server
#
# Copyright (C) 2016 argoneus <argoneuscze@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Install dependencies in case one is missing

import sys
import subprocess
import argparse
import os
import re
import subprocess
import sys
import yaml

from collections import OrderedDict

class NoAliasDumper(yaml.dumper.SafeDumper):
    """
    Makes sure a little annoyance of the super-complicated
    YAML format doesn't sneak into our innocent YAML files.
    """
    def ignore_aliases(self, _data):
        return True

def check_deps():
    import sys
    py_version = sys.version_info
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 7):
        print("tsuserverCC requires at least Python 3.7! Your version: {}.{}"
                .format(py_version.major, py_version.minor))
        sys.exit(1)
		
    try:
        import geoip2
    except ModuleNotFoundError:
        print('Installing dependencies for you...')
        try:
            import sys, subprocess
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--user', '-r',
                'requirements.txt'
                ])
            print('If an import error occurs after the installation, try '
                    'restarting the server.')
        except subprocess.CalledProcessError:
            print('Couldn\'t install it for you, because you don\'t have pip, '
                'or another error occurred.')


# So this seems to be where the whole server kicks off. If we want the YAML builder to
# fire properly, this'd be a good starting point. main() will ALWAYS launch first, so we want
# that function to call our stuff first before server.start() runs!
# -Steel

# Time to make some developers very very sad.
# Straight copy-paste of music2yaml.py into this.
# Let's work some magic! -Steel

# This lazy hack allows the ordering of items in the YAML to be preserved.
# Special thanks to https://stackoverflow.com/a/21912744/2958458

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    # Remember, we're inside a def right now
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)

    return yaml.load(stream, OrderedLoader)

def ordered_dump(data, stream=None, Dumper=NoAliasDumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

def music2yaml(yaml_path, path):

    # This is literally just the main part of the music2yaml.py script pasted into main().
    # We do a grind through music, put together our music list, then the server launches.
    # Iiiiii think. XYZ may wanna take a look at this too, my C++-fu is way better than my Python Style.
    # -Steel

    # First thing's first, updated the yaml_path so, instead of just checking for music.yaml,
    # it instead checks for our install path, then adds on /config/music.yaml. This is made with the assumption that
    # start_server.py is being run from the same folder base AND config are in!
    # I mean... I'd be surprised if it wasn't, that's why it's hardcoded. -Steel

    # Parse arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-n", "--no-new", action="store_true", help="do not add new songs to the music.yaml")
    parser.add_argument("-s", "--new-only", action="store_true", help="only scan for new songs")

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(1)

    no_new = args.no_new
    new_only = args.new_only

    if no_new and new_only:
        print("error: --no-new and --new-only flags conflict. Please only choose one.")
        sys.exit(1)

    # Since this is being run from start_server.py now, instead of a script we can just throw anywhere,
    # probably best we have a sturdy path to operate from. Basically, path will be:
    # <Path leading to the folder this script is run from> + /base/sounds/music.

    #if path.split("\\")[-1] != "/base/sounds/music":
    #    print("error: You need to run this script from the music folder.")
    #    sys.exit(1)

    # Read/parse music.yaml
    config = None
    try:
        with open(yaml_path, "r") as yaml_file:
            config = ordered_load(yaml_file.read())
    except OSError:
        print(f"The YAML file {yaml_path} could not be opened. A new one will be created.")

    # config will be none if the file could not be loaded or a blank file was loaded.
    if config is None:
        config = []

    # Extract song objects from each category
    songs = []
    for category in config:
        for track in category["songs"]:
            songs.append(track)
    song_names = [s["name"] for s in songs]

    # Check if there is a category called "Uncategorized"
    # If not, create one
    uncategorized_category = [c for c in config if c["category"] == "Uncategorized"]
    uncategorized_category_present = True
    if len(uncategorized_category) == 0:
        uncategorized_category_present = False
        uncategorized_category = OrderedDict([
            ("category", "Uncategorized"), ("songs", [])
        ])
    else:
        uncategorized_category = uncategorized_category[0]

    file_list = os.listdir(os.getcwd())
    if new_only:
        file_list = [f for f in file_list if f not in song_names]

    progress = 0
    progress_max = len(file_list)
    for file in file_list:
        progress += 1
        if file.split(".")[-1] not in ("mp3", "wav", "ogg", "opus"):
            continue
        try:
            # Invoke ffprobe to extract the length
            process = subprocess.Popen(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", file],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            out, err = process.communicate()
            length = float(out.decode("utf-8").strip().split("\r\n")[0])

            # Compose song/track object
            track = OrderedDict([
                ("name", file), ("length", length)
            ])

            # There could theoretically be the same song in multiple categories.
            # We'll cover the case just for the sake of it.
            entries = [s for s in songs if s["name"] == file]

            # Check if the song is in the list
            if len(entries) != 0:
                # Update the length property in each song entry
                # that matched the name criterion
                for entry in entries:
                    entry["length"] = track["length"]
            elif not no_new:
                # Add it to the uncategorized category
                uncategorized_category["songs"].append(track)

            print(f"({progress}/{progress_max}) {file}" + " " * 15 + "\r", end="")
        except ValueError:
            print(f"Could not open track {file}. Skipping.")
        except KeyboardInterrupt:
            print()
            print("Scan aborted! No changes have been written to disk.")
            sys.exit(2)

    print("Music.yaml path: " + yaml_path)
    print("Scan complete in folder: " + path + " " * 20)

    # Add the uncategorized category if it was used
    if not uncategorized_category_present and len(uncategorized_category["songs"]) != 0:
        config.append(uncategorized_category)

    dump = ordered_dump(config, default_flow_style=False)

    # Write the final config to file if everything went well
    with open(yaml_path, "w") as yaml_file:
        yaml_file.write(dump)
    


def character2yaml(yaml_path, path):
    print("yaml_path: " + yaml_path)
    print ("path: " + path)

    # Read/parse characters.yaml
    config = None
    try:
        with open(yaml_path, "r") as yaml_file:
            config = ordered_load(yaml_file.read())
    except OSError:
        print(f"The YAML file {yaml_path} could not be opened. A new one will be created.")

    # Note from music2yaml.py: "config will be none if the file could not be loaded or a blank file was loaded."
    if config is None:
        config = []

    print("\nconfig:")
    print(config)
    # Extract character names from the YAML. I think this should do it.
    # music2yaml does it via category, then song (category inside category), then track (which is a name and a length).
    # track's 'name' is then dumped into song_names, but I don't think we need to do that.
    chars = []
    for character in config:
        chars.append(character)

    print("\nchars:")
    print(chars)
    # We don't need to do as much categorization work as music,
    # Plus, we only want to add new characters.

    file_list = os.listdir(path)
    file_list = [f for f in file_list if f not in chars]

    print("\nfile_list:")
    print(file_list)
    # Now we're looking for folder names, not specific files.

    characters = []
    progress = 0
    progress_max = len(file_list)
    for file in file_list:
        progress += 1
        try:
            # Just build the characters list, really.
            
            print("\ncharacter: ")
            print(file)
            print(f"({progress}/{progress_max}) {file}" + " " * 15 + "\r", end="")
            
            config.append(file)

            print("\ncharacters: ")
            print(config)

        except KeyboardInterrupt:
            print()
            print("Scan aborted, no changes written to disk.")
            sys.exit(2)

    print ("Character scan complete." + " " * 20)

    # Now we just write everything to the file.

    dump = ordered_dump(config, default_flow_style=False)

    print("dump:\n")
    print(dump)
    # Aaand write it
    with open(yaml_path, "w") as yaml_file:
        yaml_file.write(dump)

def main():
    # os.getcwd() is giving me a headache, so I'm going to make things a little easier on myself,
    # and use some variables.

    # Alright Python. CAN YOU SEE /THE ROOT FUCKING DIRECTORY?/

    #print("self.path: " + self.path())
    print("os.getcwd(): " + os.getcwd())
    print("os.path.join for music.yaml" + os.path.join(os.getcwd(),"/tsuserver3cc-musicautoscan/OLEAO-ServerCC/config/music.yaml"))

    music_yaml_path = os.path.join(os.getcwd(),"/tsuserver3cc-musicautoscan/OLEAO-ServerCC/config/music.yaml")
    music_path = os.path.join(os.getcwd(),"/tsuserver3cc-musicautoscan/OLEAO-ServerCC/base/sounds/music")

    char_yaml_path = os.path.join(os.getcwd(),"/tsuserver3cc-musicautoscan/OLEAO-ServerCC/config/characters.yaml")
    char_path = os.path.join(os.getcwd(),"/tsuserver3cc-musicautoscan/OLEAO-ServerCC/characters")

    print("os.path.dirname: " + os.path.dirname(__file__))
    print("music_yaml_path: " + music_yaml_path)
    print("music_path: " + music_path)
    print("char_yaml_path: " + char_yaml_path)
    print("char_path: " + char_path)
    #yaml_path = "/music.yaml"
    #path = "/characters/"

    sys.exit(2)

    music2yaml(music_yaml_path, music_path)
    character2yaml(char_yaml_path, char_path)

    #music2yaml(yaml_path, path)
    #character2yaml(yaml_path, path)

    from server.tsuserver import TsuServerCC
    server = TsuServerCC()
    server.start()

if __name__ == '__main__':
    print('tsuserverCC - an Attorney Online server')
    check_deps()
    main()