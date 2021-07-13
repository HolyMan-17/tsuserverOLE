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
import ffmpeg

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

# Hey look, a really cool progress bar thingy :o. Stackoverflow is great, man. -Steel
def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

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
    build_new_file = False # Steel: Setting this for category building later.
    config = None
    try:
        with open(yaml_path, "r") as yaml_file:
            config = ordered_load(yaml_file.read())
    except OSError:
        print(f"The YAML file {yaml_path} could not be opened. A new one will be created.")

    # config will be none if the file could not be loaded or a blank file was loaded.
    if config is None:
        build_new_file = True
        config = []

    # Extract song objects from each category
    songs = []
    for category in config:
        for track in category["songs"]:
            songs.append(track)
    song_names = [s["name"] for s in songs]

    # Steel: Alright, so now there's another step we need to build here. First, a dictionary of categories.
    # I'm using the key here because that's what's present in the file name of the songs we're checking.
    # That way, I can just snap up the value from that key, which is the category we want it to end up in.

    tags_categories = dict([
                ("[AA]", "Ace Attorney"),
                ("[JFA]", "Justice For All"),
                ("[T&T]", "Trials & Tribulations"),
                ("[DGS]", "DGS"),
                ("[DGS2]", "DGS 2"),
                ("[AJ]", "Apollo Justice"),
                ("[AAHD]", "Ace Attorney HD"),
                ("[AAI]", "Ace Attorney Investigations"),
                ("[AAI2]", "Ace Attorney Investigations 2"),
                ("[DD]", "Dual Destinies"),
                ("[GT]", "Ghost Trick"),
                ("[JAZZ]", "Jazz"),
                ("[LBMR]", "LBMR"),
                ("[PIANO]", "Piano"),
                ("[PL]", "Professor Layton"),
                ("[SoJ]", "Spirit of Justice"),
                ("[STAFF]", "STAFF"),
                ("~stop", "STOP")
            ])
    
    
    # Steel: Now, we need to iterate through categories in music.yaml and see if they're there. If not, build them.
    # -We should really only do this if we're building a new music.yaml file, I figure it'll get out of order otherwise.

    if build_new_file:
        # Steel: We're building a new file, so let's set up our framework.
        tags_categories_songs = []

        # Iterate through each category in our 'categories' list, then create a new
        # OrderedDict object that we'll later stock up with songs.
        # We'll leave Uncategorized out, so we can make the object at the end, then append it to
        # the end of tags_categories_songs for later file writing.
        for k,v in sorted(tags_categories.items()):
            tags_categories_songs.append(
                OrderedDict([
                ("tag", str(k)), ("category", str(v)), ("songs", [])
                ])
            )
        #print(tags_categories_songs)

        file_list = os.listdir(path)
        if new_only:
            file_list = [f for f in file_list if f not in song_names]
        
        progress = 0
        progress_max = len(file_list)
        uncategorized_songs = []

        for file in progressBar(file_list, prefix = 'Progress:', suffix = 'Complete', length = 50):
            progress += 1

            if file.split(".")[-1] not in ("mp3", "wav", "ogg", "opus"):
                continue
            try:
                # First, we invoke ffprobe to extract the length, just like how it was done before.
                file_path = 'base/sounds/music/' + file

                out = subprocess.check_output(
                    ["ffprobe","-v","error","-show_entries","format=duration",
                    "-of","default=noprint_wrappers=1:nokey=1", file_path]
                )

                length = float(out.decode("UTF-8").strip().split("\r\n")[0])

                # Compose the track object we'll put into our songs categories.
                track = OrderedDict([
                    ("name", file), ("length", length)
                ])

                filename = track["name"].replace("] ", "]   ").split("  ")[0]

                # Steel: Since filename isn't going to have anything if we don't actually /get/
                # something with a square bracket in it, checking the track's name itself to see if it's ~stop.
                # Since it gets its own pretty little category in the list.
                if filename.count("[") == 0 and track.get("name").split(".")[0].lower() != "~stop":
                    #print("\nSong without a [: " + track.get("name"))
                    uncategorized_songs.append(track)
                    continue

                # We're past the uncategorized ones, now we'll just start putting categorical songs
                # in their place.
                for obj in tags_categories_songs:
                    if filename.upper() == obj.get("tag").upper() or track.get("name").split(".")[0].upper() == obj.get("tag").upper():
                        #print("\nSong with a [: " + track.get("name"))
                        obj.get("songs").append(track)
                        continue
                
                #print(f"({progress}/{progress_max}) {file}" + " " * 15 + "\r", end="")
                # Songs might show up multiple times in the list.
                # Unsure how to implement protection for this,
                # so I've brought over the original way of doing it and commented it out.
                # Just gonna have to study this later.

                # entries = [s for s in songs if s["name"] == file]

                # Check if the song's already in the file.

                #if len(entries) != 0:
                # Update the length property in each song entry
                # that matched the name criterion
                #for entry in entries:
                #    entry["length"] = track["length"]

                #elif not no_new:
                    # Add it to the uncategorized category
                #    uncategorized_category["songs"].append(track)

                # Alright, we have our track objects. Let's add them to the list...
            except ValueError as ve:
                print("ValueError: " + str(ve))
                print(f"Could not open track {file_path}. Skipping.")

            except KeyboardInterrupt:
                print("don't interrupt me I'm workin' :c -Steel")
                print("Also not writing anything to file. Dumping everything we've done so far.")

        uncategorized_category = OrderedDict([("tag", ""), ("category", "Uncategorized"), ("songs", [])])

        if len(uncategorized_songs) != 0:
            for song in uncategorized_songs:
                uncategorized_category.get("songs").append(song)
                # Steel: Behold this ungodly abomination because I can't figure out
                # how to grab a freakin' OrderedDict object from a list, insert into it,
                # then put it back neatly. Worst librarian :(.
        else:
            print("No uncategorized songs.")

        #print("\n\n\nUncategorized Songs")
        #print(uncategorized_category.get("songs"))

        # Steel: Alright, now we have our filled up categories... let's assemble it all together, then push
        # to a new music.yaml file!

        for obj in tags_categories_songs:
            config.append(obj)

        config.append(uncategorized_category)

        #print(config)

        dump = ordered_dump(config, default_flow_style=False)

        #print(dump)

        # Steel: And thus, when Steel did run dir config on the server...
        # he did indeed find a new music.yaml file. Nice to have this actually work.
        with open(yaml_path, "w") as yaml_file:
            yaml_file.write(dump)

    else:
        #Else NOTHING right now, good God I need to make sure the building works first!
        print("Not doing anything to the music.yaml file right now, this part's under construction.\n-Foreman Steel")
    


    # Check if there is a category called "Uncategorized"
    # If not, create one
    #uncategorized_category = [c for c in config if c["category"] == "Uncategorized"]
    #uncategorized_category_present = True
    #if len(uncategorized_category) == 0:
    #    uncategorized_category_present = False
    #    uncategorized_category = OrderedDict([
    #        ("category", "Uncategorized"), ("songs", [])
    #    ])
    #else:
    #    uncategorized_category = uncategorized_category[0]

    #file_list = os.listdir(path)
    #if new_only:
    #    file_list = [f for f in file_list if f not in song_names]

    #progress = 0
    #progress_max = len(file_list)
    #for file in file_list:
    #    progress += 1
    #   #print("Progress: " + str(progress))

    #    if file.split(".")[-1] not in ("mp3", "wav", "ogg", "opus"):
    #        continue
    #    try:
    #        # Invoke ffprobe to extract the length
    #        file_path = 'base/sounds/music/' + file
            
    #        out = subprocess.check_output(
    #            ["ffprobe","-v","error","-show_entries","format=duration",
    #            "-of","default=noprint_wrappers=1:nokey=1", file_path])
            
    #        length = float(out.decode("UTF-8").strip().split("\r\n")[0])

            # Compose song/track object
    #        track = OrderedDict([
    #            ("name", file), ("length", length)
    #        ])

            # There could theoretically be the same song in multiple categories.
            # We'll cover the case just for the sake of it.
    #        entries = [s for s in songs if s["name"] == file]

            # Check if the song is in the list
    #        if len(entries) != 0:
                # Update the length property in each song entry
                # that matched the name criterion
    #            for entry in entries:
    #                entry["length"] = track["length"]

    #        elif not no_new:
                # Add it to the uncategorized category
    #            uncategorized_category["songs"].append(track)

    #        print(f"({progress}/{progress_max}) {file}" + " " * 15 + "\r", end="")
    #    except ValueError as ve:
    #       print("ValueError: " + str(e))
    #        print(f"Could not open track {file_path}. Skipping.")

    #    except subprocess.CalledProcessError as cpe:
    #        raise RuntimeError("command '{}' return with error (code {}): {}".format(cpe.cmd, cpe.returncode, cpe.output))
     #       print("Ran into a process error.")

     #   except ffmpeg.Error as ff:
    #        print(ff.stderr)

    #    except KeyboardInterrupt:
     #       print("Scan aborted! No changes have been written to disk.")
     #       sys.exit(2)

    #print("Music.yaml path: " + yaml_path)
    #print("Scan complete in folder: " + path + " " * 20)

    # Add the uncategorized category if it was used
    #if not uncategorized_category_present and len(uncategorized_category["songs"]) != 0:
    #   config.append(uncategorized_category)

    #dump = ordered_dump(config, default_flow_style=False)

    #print(dump)

    # Write the final config to file if everything went well
    #with open(yaml_path, "w") as yaml_file:
    #    yaml_file.write(dump)
    


def character2yaml(yaml_path, path):
    #print("yaml_path: " + yaml_path)
    #print ("path: " + path)

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

    #print("\nconfig:")
    #print(config)
    # Extract character names from the YAML. I think this should do it.
    # music2yaml does it via category, then song (category inside category), then track (which is a name and a length).
    # track's 'name' is then dumped into song_names, but I don't think we need to do that.
    chars = []
    for character in config:
        chars.append(character)

    #print("\nchars:")
    #print(chars)
    # We don't need to do as much categorization work as music,
    # Plus, we only want to add new characters.

    file_list = os.listdir(path)
    file_list = [f for f in file_list if f not in chars]

    #print("\nfile_list:")
    #print(file_list)
    # Now we're looking for folder names, not specific files.

    progress = 0
    progress_max = len(file_list)
    for file in progressBar(file_list, prefix = 'Progress:', suffix = 'Complete', length = 50):
        progress += 1
        try:
            # Just build the characters list, really.
            
            if "." not in file:
                config.append(file)
                #print(f"({progress}/{progress_max}) {file}" + " " * 15 + "\r", end="")
                #print("Progress {progress}: " + file)

        except KeyboardInterrupt:
            print()
            print("Scan aborted, no changes written to disk.")
            sys.exit(2)

    print ("Character scan complete." + " " * 20)

    # Now we just write everything to the file.

    dump = ordered_dump(sorted(config), default_flow_style=False)

    #print("dump:\n")
    #print(dump)
    # Aaand write it
    with open(yaml_path, "w") as yaml_file:
        yaml_file.write(dump)

def main():
    # os.getcwd() is giving me a headache, so I'm going to make things a little easier on myself,
    # and use some variables.

    # Alright Python. CAN YOU SEE /THE ROOT FUCKING DIRECTORY?/

    #print("self.path: " + self.path())
    #print("os.getcwd(): " + os.getcwd())
    #print("os.path.join for music.yaml: " + os.path.join(os.getcwd(),"/tsuserver3cc-musicautoscan/OLEAO-ServerCC/config/music.yaml"))

    music_yaml_path = os.path.join(os.getcwd(),"config/music.yaml")
    music_path = os.path.join(os.getcwd(),"base/sounds/music")

    char_yaml_path = os.path.join(os.getcwd(),"config/characters.yaml")
    char_path = os.path.join(os.getcwd(),"characters")

    music2yaml(music_yaml_path, music_path)
    character2yaml(char_yaml_path, char_path)

    from server.tsuserver import TsuServerCC
    server = TsuServerCC()
    server.start()

if __name__ == '__main__':
    print('tsuserverCC - an Attorney Online server')
    check_deps()
    main()