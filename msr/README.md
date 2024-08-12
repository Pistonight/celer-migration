# Migration Example - MSR

The MSR example has the following directory structure:
```
- msr
  - main.celer
```

In the end, we will migrate it to new celer, which will have this structure:
```
- msr-new
  - project.yaml
  - main.yaml
  - check-pepper.yaml
  - branches
    - start.yaml
    - akkala.yaml
    - ridgeland.yaml
```

## 1. Metadata
The first step is to migrate the metadata. This is `_project` from old celer:
```yaml
# file: main.celer
_project: 
  name: Master Sword Restricted
  authors:
    - iTNTPiston
  version: "3.0"
  description: Get Master Sword without glitches that allow you to get it early
  url: ""
```

Create a directory `msr-new` in the repo root, and create a `project.yaml` file with the following content:
```yaml
title: Master Sword Restricted
version: v3.0

route:
  use: ./main.yaml
```

## 2. Main Route Structure
The second step is to migrate the main route structure. This is the `_route` from old celer. The next block only shows the structure, not the entire content:
```yaml
# file: main.celer

_route:
  - (==) This is a newer version of the route inspired by ...
  - Dueling Peaks + Faron + Lake:
    - ... (not shown)
  - Akkala:
    - ... (not shown)
  - Ridgeland:
    - ... (not shown)
```
To migrate this structure, run the following command from the root of the repo

```bash
python celer-migrate.py msr/main.celer --main
```
This should emit 4 new files. The tool doesn't know how to name the files, so they will have generated names.
Create a new `branches` directory inside `msr` (not `msr-new`), and move/rename the files like so:
```
main.celer_main.yaml           --> move to msr-new/main.yaml
main.celer_main.section.1.yaml --> move to msr/branches/start.yaml
main.celer_main.section.2.yaml --> move to msr/branches/akkala.yaml
main.celer_main.section.3.yaml --> move to msr/branches/ridgeland.yaml
```
Now the directory structure should look like this:
```
- msr
  - main.celer
  - branches
    - start.yaml
    - akkala.yaml
    - ridgeland.yaml
- msr-new
  - project.yaml
  - main.yaml
```
Open `msr-new/main.yaml` and delete all the metadata. The result should be something like this:
```yaml
- This is a newer version of the route inspired by .code(@MikeysGone). If you
  are looking for the Mogg Latan route. Go .link([here]https://celer.itntpiston.app/#/gh/iTNTPiston/msr/mogg-latan)
- Dueling Peaks + Faron + Lake:
  - use: msr/main.celer_main.section.1.yaml
- Akkala:
  - use: msr/main.celer_main.section.2.yaml
- Ridgeland:
  - use: msr/main.celer_main.section.3.yaml
```
Finally, rename the `use:` paths to `./branches/XXX.yaml`, which we will migrate in the next section:
```yaml
- This is a newer version of the route inspired by .code(@MikeysGone). If you
  are looking for the Mogg Latan route. Go .link([here]https://celer.itntpiston.app/#/gh/iTNTPiston/msr/mogg-latan)
- Dueling Peaks + Faron + Lake:
  - use: ./branches/start.yaml
- Akkala:
  - use: ./branches/akkala.yaml
- Ridgeland:
  - use: ./branches/ridgeland.yaml
```
## 3. Migrate each Branch
Run the following command
```bash
python celer-migrate.py msr/branches
```
This will create a new `_new.yaml` file for each branch `yaml` file.

Open `branches/start.yaml_new.yaml`. You will see a lot of places like this:
```
>>>>>>>>>>>>>
>>>>>>>>>>>>> FIXME: split-type
- Plateau:
    icon: king
    split-type: UserDefined
    coord: [-812, 1965.07]
>>>>>>>>>>>>> FIX ERRORS ABOVE
>>>>>>>>>>>>>
```
This is because `split-type` is replaced by `counter` in new celer. To fix this, let's add a custom split type to `project.yaml`. For more information on how splitting works, see https://celer.pistonite.org/docs/route/counter-and-splits

Add the following to `project.yaml`:
```yaml
config:
- tags:
    split:
      background: black
      color: white
      split-type: Custom
  splits:
  - split
```
This will add a tag type `split` with the split type `Custom`. Adding it to `splits` means it should be on by default.

Now we can fix the generated output to this:
```yaml
- Plateau:
    icon: king
    counter: .split(SPLIT) # originally: split-type: UserDefined
    coord: [-812, 1965.07]
```

The next error is
```
>>>>>>>>>>>>>
>>>>>>>>>>>>> FIXME: __use__
- __use__ CheckPepper
>>>>>>>>>>>>> FIX ERRORS ABOVE
>>>>>>>>>>>>>
```
`__use__ SECTION` is replaced by `use: FILE` in new celer. Here it's refering to a shared step to check pepper. This was in `main.celer`. Let's create `msr-new/check-pepper.yaml` with the following content:
```yaml
- At least .var(Pepper) half-heart food left
```
Note this uses the `var` tag for variable tracking. New celer no longer has variable system built-in. It's instead a plugin. Let's add this plugin in `project.yaml`
```yaml
config:
- tags:
    split:
      background: black
      color: white
      split-type: Custom
  splits:
  - split
  plugins:            # ADD THIS LINE
  - use: variable     # ADD THIS LINE
```

Now we can search and replace the above error with
```yaml
- use: ../check-pepper.yaml
```

This file is now done! Repeat the same process for the other 2 files.
Note that `ridgeland.yaml_new.yaml` has no errors, so we can skip it. `akkala.yaml_new.yaml` only has one error - the split type, we can fix it the same way we did:
```yaml
- Master Sword:
    icon: tots
    counter: .split(SPLIT)
    coord: [431.66, 250.53, -2111.0]
```

## 4. Move the files over
Run the following. Note we are running
the `celer-move.py` script, not the `celer-migrate.py` script.
```bash
python celer-move.py msr/branches msr-new/branches
```

## 5. Add Presets
Since new celer is game-independent, we need to add the BOTW presets. I will also add the `split-format` plugin to add shrine numbers to the splits:
The final `project.yaml` should look like this:
```yaml
title: Master Sword Restricted
version: v3.0

route:
  use: ./main.yaml

config:
- use: Pistonight/celer-presets/botw/most.yaml
- tags:
    split:
      background: black
      color: white
      split-type: Custom
  splits:
  - split
  plugins:
  - use: variables
  - use: split-format
    with:
      Shrines: "[.var(pad02:counter-shrine)] .prop(text)"
```

## 6. Done!
Now, load the `msr-new` project in celer editor: https://celer.pistonite.org/edit and it should load without any errors.
