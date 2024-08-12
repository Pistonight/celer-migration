# Migration Example - ASX

The ASX example has the following directory structure:
```
- asx
  - main.celer
  - common.celer
  - branches
    - Akkala.celer
    - Bloodmoon.celer
    - ...
```

In the end, we will migrate it to new celer, which will have this structure:
```
- asx-new
  - project.yaml
  - main.yaml
  - branches
    - akkala.yaml
    - bloodmoon.yaml
    - ...
```

## 1. Metadata
The first step is to migrate the metadata. This is `_project` from old celer:
```yaml
# file: main.celer
_project: 
  name: ASX Aristos v3
  authors:
    - iTNTPiston
  version: 3.1.0
  description: All Shrines Extended
  url: "https://github.com/iTNTPiston/asx"
```

Create a directory `asx-new` in the repo root, and create a `project.yaml` file with the following content:
```yaml
title: All Shrines Extended
version: v3.1.0

route:
  use: ./main.yaml
```

## 2. Main Route Structure
The ASX project is structured in this way:
- `main.celer` contains the order of branches
- `branches` folder contain one `celer` file for each branch

Create `asx-new/main.yaml` and copy over `_route` from `asx/main.celer`.
Then do a search and replace to change `__use__ SECTION` to `use: ./branches/SECTION.yaml`.
For example, in VS Code, you can use the following regex:
```
Search: __use__ (.+)
Replace: use: ./branches/$1.yaml
```
After fixing the syntax, `main.yaml` should look like this:
```yaml
- Plateau:
  - use: ./branches/Plateau.yaml
- Hateno:
  - use: ./branches/Hateno.yaml
- Korok Forest:   
  - use: ./branches/Plateau2.yaml
  - use: ./branches/KorokForest.yaml
- Highland:
  - use: ./branches/Hebra.yaml
  - use: ./branches/Gerudo.yaml
- Eldin:
  - use: ./branches/ZD.yaml
  - use: ./branches/Eldin.yaml
- Akkala:
  - use: ./branches/Bloodmoon.yaml
  - use: ./branches/Akkala.yaml
- Wasteland:
  - use: ./branches/Wasteland.yaml
- Central:
  - use: ./branches/Central.yaml
```

## 3. Migrate each Branch
Run the following command
```bash
python celer-migrate.py asx/branches
```
**Note**: If at this step, you see an error like "XXX has more than one section", it means the `celer` file contains more than one section, like this:
```yaml
SECTION 1:
- ...
- ...

SECTION 2:
- ...
- ...
```

In this case, you need to manually split the sections into separate files, give them `.celer` or `.yaml` extensions, and run the tool again.

This step will create a new `_new.yaml` file for each branch `celer` file.

Open `asx/branches/Plateau.celer_new.yaml`. Note that there are 3 errors at the end with `FIXME`.

The first is because `split-type` is replaced by `counter` in new celer. To fix this, let's add a custom split type to `project.yaml`. For more information on how splitting works, see https://celer.pistonite.org/docs/route/counter-and-splits

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

Now replace
```
>>>>>>>>>>>>>
>>>>>>>>>>>>> FIXME: split-type
- Plateau:
    icon: king
    split-type: UserDefined
    coord: [-812, 1966.1012189378007]
>>>>>>>>>>>>> FIX ERRORS ABOVE
>>>>>>>>>>>>>
```
with
```yaml
- Plateau:
    icon: king
    counter: .split(SPLIT)
    coord: [-812, 1966.1012189378007]
```

For the other two, it's using the old `__use__` syntax. The route is trying
to use a shared step to check wood, arrows, and slots. In new celer, we can now do
that through custom presets.

The old steps can be found in `asx/common.celer`:
```yaml
CheckSlots:
  .v(Weapons)/8 Weapons
CheckWoodAndArrows:
  .v(Wood) wood left:
    notes: .v(Arrow) Normal Arrow; .v(IceArrow) Ice; .v(FireArrow) Fire
```
When translated to presets in new celer, it should look like this:
```yaml
CheckSlots:
  text: .var(Weapons)/8 Weapons
CheckWoodAndArrows:
  text: .var(Wood) wood left
  notes: .var(Arrow) Normal Arrow; .var(IceArrow) Ice; .var(FireArrow) Fire
```
Note that `.v` is changed to `.var`.

Add to `config` in `project.yaml` the following. Make sure the intentation is correct.
```yaml
config:
- tags:
    split:
      background: black
      color: white
      split-type: Custom
  splits:
  - split
  # ADD THE BELOW
  plugins:
  - variables
  presets:
    _Check:
      Slots:
        text: .var(Weapons)/8 Weapons
      WoodAndArrows:
        text: .var(Wood) wood left
        notes: .var(Arrow) Normal Arrow; .var(IceArrow) Ice; .var(FireArrow) Fire

```
Here, we added 2 presets and the `variables` plugin to use the variable system with the `var` tag.

Now we can fix the error in the route by replacing
```
>>>>>>>>>>>>>
>>>>>>>>>>>>> FIXME: __use__
- __use__ CheckWoodAndArrows
>>>>>>>>>>>>> FIX ERRORS ABOVE
>>>>>>>>>>>>>
>>>>>>>>>>>>>
>>>>>>>>>>>>> FIXME: __use__
- __use__ CheckSlots
>>>>>>>>>>>>> FIX ERRORS ABOVE
>>>>>>>>>>>>>
```
with
```yaml
- _Check::WoodAndArrows
- _Check::Slots
```
Since this check is used throughout the route, go ahead and search & replace in other branch files as well. If your editor doesn't support search/replace. Please use
[VS Code](https://code.visualstudio.com/Download)

There are actually only a few errors left. Open `asx/branches/Hateno.celer_new.yaml`
and fix the `split-type` error:
```yaml
- Camera:
    comment: Throw away torch if you got
    icon: snap
    notes: .var(Weapons)/8 Weapons
    counter: .split(SPLIT)   # was: split-type: UserDefined
    vars:
      Weapons: .sub(1)
    coord: [3779, 2124.8845192940553]
```

Finally, open `asx/branches/Central.celer_new.yaml` and fix the same `split-type` errors for the last 3 splits

**Note**: If your route has gale/fury usage, although it should be rare, it's possible there is another error for route like this:
```yaml
- .fury() something, really .fury() it:
    fury: 1
```
In old celer, both `.fury()` will refer to the same 2 furies used, so this will become:
```yaml
FURY 1 something, really FURY 1 it
```
In new celer, the second fury will be a different fury, so this will become:
```yaml
FURY 1 something, really FURY 2 it
```
This needs to fixed manually. If the step only has one instance of `.fury()` or `.gale()`, then it's not an issue.

## 4. Move the files over
Run the following. Note we are running
the `celer-move.py` script, not the `celer-migrate.py` script.
```bash
python celer-move.py asx/branches asx-new/branches
```
## 5. Add Presets
Since new celer is game-independent, we need to add the BOTW presets to `project.yaml`. You can also add other plugins and configs here such as `split-format`.
```yaml
config:
- use: Pistonight/celer-presets/botw/most.yaml
### ^^^ ADD THIS LINE
- tags:
    split:
      background: black
      color: white
      split-type: Custom
  splits:
  - split
  plugins:
  - use: variables
  presets:
    _Check:
      Slots:
        text: .var(Weapons)/8 Weapons
      WoodAndArrows:
        text: .var(Wood) wood left
        notes: .var(Arrow) Normal Arrow; .var(IceArrow) Ice; .var(FireArrow) Fire
```

## 6. Done
Now, load the `asx-new` project in celer editor: https://celer.pistonite.org/edit and it should load without any errors.
