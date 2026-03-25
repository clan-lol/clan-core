# How to Rename a Clan Machine

:::admonition[You probably shouldn't do this]{type=warning}
Machine names are **immutable by design**. Once a name hits your infrastructure, it becomes deeply embedded in secrets, vars, service references, and other machines' configs. Best practice in DevOps is to burn a name. If you decommission a machine, retire the name with it and pick a fresh one for its replacement.

If you still need to deeply rename a machine, the steps below will get you there.
:::

Renaming `oldbox` to `newbox`.

## Where the name lives

| Place | Path |
|-------|------|
| Machine directory | `machines/<name>/` |
| Vars | `vars/per-machine/<name>/` |
| Inventory | `flake.nix`, `inventory.machines`, `inventory.instances` |
| Other machines | `.nix` files that mention this machine by name |
| Secrets | `sops/` directories and symlinks, passage, etc. |

## 1. Grep first

```bash
grep -rn "oldbox" --include="*.nix" --include="*.json" .
```

Zero hits outside the machine's own directory means a simple rename (steps 2 to 5).

## 2. Rename the machine directory

```bash
mv -T machines/oldbox machines/newbox
```

Clan discovers machines by directory name.

The `-T` flag prevents `mv` from putting `oldbox` inside an existing `newbox` directory.

## 3. Rename the vars and sops directories

```bash [rename.sh] {1-2}
OLDNAME=nas
NEWNAME=bob

mv -T vars/per-machine/$OLDNAME vars/per-machine/$NEWNAME

for d in sops/secrets/$OLDNAME-*; do
    mv -T "$d" "${d/$OLDNAME-/$NEWNAME-}"
done

# fixup symlinks
find sops/ -type l -lname "*machines/$OLDNAME*" | while read link; do
    dir=$(dirname "$link")
    target=$(readlink "$link" | sed "s|machines/$OLDNAME|machines/$NEWNAME|")
    rm "$link"
    ln -s "$target" "$dir/$NEWNAME"
done

find vars/ -type l -lname "*machines/$OLDNAME*" | while read link; do
    dir=$(dirname "$link")
    target=$(readlink "$link" | sed "s|machines/$OLDNAME|machines/$NEWNAME|")
    rm "$link"
    ln -s "$target" "$dir/$NEWNAME"
done
```

If you are using `password-store` instead of sops do this

```bash
OLDNAME=oldbox
NEWNAME=newbox

mv -T vars/per-machine/$OLDNAME vars/per-machine/$NEWNAME

for d in sops/secrets/$OLDNAME-*; do
    mv -T "$d" "${d/$OLDNAME-/$NEWNAME-}"
done

# If you use 'pass'
pass mv machines/oldbox machines/newbox

# If you use 'passage'
passage mv machines/oldbox machines/newbox
```

## 4. Update the machine's own config

In `machines/newbox/configuration.nix`:

```diff
-  networking.hostName = "oldbox";
+  networking.hostName = "newbox";
```

If you set `targetHost`:

```diff
-  clan.core.networking.targetHost = "root@oldbox";
+  clan.core.networking.targetHost = "root@newbox";
```

## 5. Update the inventory

Rename the machine key and fix service role assignments in `flake.nix`:

```diff
 inventory = {
   machines = {
-    oldbox.tags = [ "server" ];
+    newbox.tags = [ "server" ];
   };
   instances = {
     some-service = {
       roles.server.machines = {
-        oldbox = {};
+        newbox = {};
       };
     };
   };
 };
```

## 6. Fixup cross-references

Go through the grep output from step 1 and update every reference in other
machines' configs, shared modules, DNS zone files, nginx configs, etc.

Check nothing is left:

```bash
grep -rn "oldbox" --include="*.nix" --include="*.json" . | grep -v '.git/'
```

## 8. Stage and check

```bash
git add --all
```

```bash
clan machines list
```

Verify `newbox` appears and `oldbox` does not.

## 9. Regenerate vars

After renaming, vars may be out of date. Regenerate them for your entire clan:

```bash
clan vars generate --regenerate
```

Or, if you prefer to limit the scope, regenerate only for the affected machines:

```bash
clan vars generate newbox --regenerate
```

:::admonition[Why regenerate?]{type=info}
Vars (secrets, keys, tokens) may contain references to the old machine name or may have been generated in a context that assumed the old name. Regenerating ensures everything is consistent with the new name.
:::

## 10. Final verification

```bash
clan vars list newbox
nix eval .#nixosConfigurations.newbox.config.networking.hostName
nix eval .#nixosConfigurations.newbox.config.system.build.toplevel.drvPath

find sops/ vars/ -type l ! -exec test -e {} \; -print 2>/dev/null
# Check for any broken symlink
grep -rn "oldbox" --include="*.nix" --include="*.json" . | grep -v '.git/'
# Check if the old name is still referenced
```
