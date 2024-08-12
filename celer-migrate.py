#!/usr/bin/env python3
# Scan for legacy celer attributes:
#   line-color
#   hide-icon-on-map
#   split-type
#   var-change
#   __use__

# It could make mistakes, so it will output the file as file.new.yaml next to the input
# and you can manually fix the issues
# for issues it can't fix, it will output a notice next to the line

import os
import yaml
import sys



def process_path(path, undo):
    if os.path.isfile(path):
        #print(path)
        if path.endswith("_new.yaml"):
            #print("? "+ path[:-9])
            if os.path.isfile(path[:-9]):
                if undo:
                    os.remove(path)
                return
        if path.endswith(".yaml") or path.endswith(".yml") or path.endswith(".celer"):
            process_file(path)
        return
    for subpath in os.listdir(path):
        subpath = os.path.join(path, subpath)
        process_path(subpath, undo)

def process_main(path):
    print("main -- "+ path)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    route = data["_route"]
    if not isinstance(route, list):
        route = [route]
    section_idx = 1
    for i, section in enumerate(route):
        if not isinstance(section, dict):
            if isinstance(section, str):
                for tag in ("(==)", "(?=)", "(!=)", "(^=)", "(?^)", "(^?)", "(!^)", "(^!)"):
                    if tag in section:
                        section = section.replace(tag, "")
                route[i] = section.strip()
            continue
        if len(section) != 1:
            continue
        key = next(iter(section))
        section_data = section[key]
        if not isinstance(section_data, list):
            section_data = [section_data]
        section_path = path+"_main.section."+str(section_idx)+".yaml"
        with open(section_path, "w", encoding="utf-8") as f:
            f.write(yaml.dump({key:section_data}, None, indent=2))
        section_data = [{"use": section_path}]
        route[i] = {key: section_data}
        section_idx += 1
    with open(path+"_main.yaml", "w", encoding="utf-8") as f:
        f.write(yaml.dump(data, None, indent=2))

def process_file(path):
    print("-- "+ path)
    segments = parse_file_into_segments(path)
    if len(segments) != 1:
        print("ERROR: "+path+" has more than one section (one starting with SECTION_NAME:). Please separate them to multiple files manually and try again")
        return
    out_lines = []
    (_, segment) = segments[0]
            
    for step in segment:
        old_dump = yaml.dump(step, None, indent=2).split("\n")
        new_step = fix_segment(step)
        if new_step:
            out_lines.extend(new_step)
        else:
            out_lines.extend(["", ">>>>>>>> FAIL TO PARSE"])
            out_lines.extend(old_dump)
            out_lines.extend(["", ">>>>>>>> FIX PARSING ERROR ABOVE", ""])
    with open(path+"_new.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join([x.rstrip() for x in out_lines if x.rstrip()]))

def parse_file_into_segments(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        if not isinstance(data, dict):
            return None
        segments = []
        for name in data:
            segment = data[name]
            if not isinstance(segment, list):
                segment = [segment]
            segments.append((name, segment))
    return segments

def fix_segment(data):
    if not isinstance(data, dict):
        if not isinstance(data, str):
            return None
        key = data
        value = {}
    else:
        if len(data) != 1:
            return None
        key = next(iter(data))
        value = data[key]
    if not isinstance(value, dict):
        return None
    new_value = {}
    has_icon = False
    has_hide_icon_on_map = False
    unfixable = set()
    has_gale = False
    has_fury = False
    for prop in value:
        if prop == "line-color":
            new_value["color"] = value[prop]
        elif prop == "hide-icon-on-map":
            has_hide_icon_on_map = True
        elif prop == "icon":
            has_icon = True
        elif prop == "split-type":
            unfixable.add("split-type")
            new_value["split-type"] = value[prop]
        elif prop == "var-change":
            new_value["vars"] = {}
            try:
                for var in value[prop]:
                    old_var_value = int(value[prop][var])
                    if old_var_value < 0:
                        new_value["vars"][var] = ".sub(" + str(-old_var_value) + ")"
                    else:
                        new_value["vars"][var] = ".add(" + str(old_var_value) + ")"
            except ValueError:
                unfixable.add("var-change")
                new_value["var-change"] = value[prop]
        elif prop == "gale":
            new_value["gale"] = value[prop]
            has_gale = True
        elif prop == "fury":
            new_value["fury"] = value[prop]
            has_fury = True
        else:
            new_value[prop] = value[prop]
    if has_icon:
        if has_hide_icon_on_map:
            new_value["icon-doc"] = value["icon"]
        else:
            new_value["icon"] = value["icon"]
    else:
        if has_hide_icon_on_map:
            new_value["icon-map"] = None
    key: str = key.replace(".!!(", ".important(")
    if key.startswith("+"):
        key = key[1:]
    if key == "_Warp::VahMedoh":
        key = "_Warp::Beast::Medoh"
    elif key == "_Warp::VahRudania":
        key = "_Warp::Beast::Rudania"
    elif key == "_Warp::VahRuta":
        key = "_Warp::Beast::Ruta"
    elif key == "_Warp::VahNaboris":
        key = "_Warp::Beast::Naboris"
    def has_string_property(p):
        return p in new_value and new_value[p] and isinstance(new_value[p], str)
    if has_string_property("comment"):
        new_value["comment"] = replace_tags(new_value["comment"])
    if has_string_property("comments"):
        new_value["comment"] = replace_tags(new_value["comments"])
        del new_value["comments"]
    if has_string_property("notes"):
        new_value["notes"] = replace_tags(new_value["notes"])
    if has_string_property("note"):
        new_value["notes"] = replace_tags(new_value["note"])
        del new_value["note"]
    if has_string_property("text"):
        new_value["text"] = replace_tags(new_value["text"])
    for tag in ("(==)", "(?=)", "(!=)", "(^=)", "(?^)", "(^?)", "(!^)", "(^!)"):
        if tag in key:
            key = key.replace(tag, "").strip()
            new_value["banner"] = True
    if has_gale:
        if key.count(".gale()") > 1:
            unfixable.add("gale (multiple in text)")
        if has_string_property("text") and new_value["text"].count(".gale()") > 1:
            unfixable.add("gale (multiple in text)")
        if has_string_property("notes") and new_value["notes"].count(".gale()") > 1:
            unfixable.add("gale (multiple in notes)")
        if has_string_property("comment") and new_value["comment"].count(".gale()") > 1:
            unfixable.add("gale (multiple in comments)")
    if has_fury:
        if key.count(".fury()") > 1:
            unfixable.add("fury (multiple in text)")
        if has_string_property("text") and new_value["text"].count(".fury()") > 1:
            unfixable.add("fury (multiple in text)")
        if has_string_property("notes") and new_value["notes"].count(".fury()") > 1:
            unfixable.add("fury (multiple in notes)")
        if has_string_property("comment") and new_value["comment"].count(".fury()") > 1:
            unfixable.add("fury (multiple in comments)")
    if "coord" in new_value:
        coord = new_value["coord"]
        if not isinstance(coord, list):
            unfixable.add("coord")
        del new_value["coord"]
    else:
        coord = None
    if "movements" in new_value:
        movements = new_value["movements"]
        if isinstance(movements, list):
            for m in movements:
                if not isinstance(m, dict):
                    unfixable.add("movements")
                    break
                if "away" in m:
                    unfixable.add("movements")
                    break
        else:
            unfixable.add("movements")
        del new_value["movements"]
    else:
        movements = None
    output = []
    if "__use__" in key:
        unfixable.add("__use__")
    
    if new_value:
        new_data = {}
        new_data[key] = new_value
    else:
        new_data = key
    
    output.extend([x.rstrip() for x in yaml.dump([new_data],None,indent=2).split("\n") if x.rstrip()])
    if not new_value and output and (coord or movements):
        output[-1] = output[-1].rstrip() + ":"
    if coord:
        if isinstance(coord, list):
            coord_str = ", ".join([str(x) for x in coord])
            output.append("    coord: ["+coord_str+"]")
        else:
            output.extend(yaml.dump({"coord": coord},None,indent=2).split("\n"))
    if movements:
        if isinstance(movements, list):
            output.append("    movements:")
            has_dash = False
            for m in movements:
                if "to" in m and isinstance(m["to"], list):
                    to_str = ", ".join([str(x) for x in m["to"]])
                    output.append("    - to: ["+to_str+"]")
                    has_dash = True
                    del m["to"]
                for prop in m:
                    v = m[prop]
                    if isinstance(v, bool) or isinstance(v, int) or isinstance(v, float) or isinstance(v, str):
                        if not has_dash:
                            output.append("    - "+prop+": "+str(m[prop]))
                            has_dash = True
                        else:
                            output.append("      "+prop+": "+str(m[prop]))
                    else:
                        d = {}
                        d[prop] = v
                        output.extend(yaml.dump(d,None,indent=2).split("\n"))
                        unfixable.add("movements."+prop)
        else:
            output.extend(yaml.dump({"movements": movements},None,indent=2).split("\n"))

    if unfixable:
        output = [
            ">>>>>>>>>>>>>",
            ">>>>>>>>>>>>> FIXME: "+", ".join(unfixable)
        ] + output + [
            ">>>>>>>>>>>>> FIX ERRORS ABOVE",
            ">>>>>>>>>>>>>"
        ]
    return output

def replace_tags(text):
    return text.replace(".!!(", ".important(").replace(".v(", ".var(")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: celer-migrate.py PATH [--undo|--main|--move]")
        sys.exit(1)
    path = sys.argv[1]
    undo = False
    if len(sys.argv) > 2 and sys.argv[2] == "--undo":
        undo = True
    main = False
    if len(sys.argv) > 2 and sys.argv[2] == "--main":
        main = True
    if main:
        process_main(sys.argv[1])
    else:
        process_path(sys.argv[1], undo)