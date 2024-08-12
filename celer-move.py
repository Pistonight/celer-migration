#!/usr/bin/env python3
import os
import sys
def move_path(src, dst, path):
    src_path = os.path.join(src, path)
    if os.path.isfile(src_path) and src_path.endswith("_new.yaml"):
        dst_path = os.path.join(dst, path[0:-9])
        if dst_path.endswith(".celer"):
            dst_path = dst_path[0:-6]+".yaml"
        if os.path.exists(dst_path):
            print("ERROR: "+dst_path+" already exists. Remove it first")
            sys.exit(1)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        print(src_path+" --> "+dst_path)
        os.rename(src_path, dst_path)
    elif os.path.isdir(src_path):
        for subpath in os.listdir(src_path):
            move_path(src, dst, os.path.join(path, subpath))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: celer-move.py <src> <dst>")
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2]
    move_path(src, dst, "")