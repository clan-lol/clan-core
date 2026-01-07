{
  clanLib,
  lib,
}:
/**
  Takes a list of types
  Returns a list of types that is the superset of all types in 'types' and
  with nested oneOfs flattened

  Example:

  types := [
    { type = "str" }
    { oneOf = [
      { $ref = {
        typeName = "ModuleA";
        jsonschema = { type = "str" };
      }
    }
  ]

  flattenOneOf types
  =>
  [ { type = "str" } ]

  ModelA would not be added to the output, since an superset of it is already contained
*/
jsonschemas:
let
  flatten = lib.foldl' (
    flattened: jsonschema:
    if jsonschema ? oneOf then flatten flattened jsonschema.oneOf else mergeType flattened jsonschema
  );

  /**
    Takes a list of existing types and a new type

    Returns a list that is guaranteed to contain all types that are distinct

    [ t1 t2 t3 ] cannot be collapsed further

    Examples

    mergeType [ str int ] str
    => [ str int]

    mergeType [ int ] (str | int)
    => [ (str | int) ]

    mergeType [ int ] str
    => [ int str ]
  */
  mergeType =
    flattened: newJsonschema:
    let
      containingIndex = lib.lists.findFirstIndex (
        # existingType ⊇ newType
        # Some existing type already contains the newType
        # => we dont need to add the newType
        existingJsonschema: isContainingType existingJsonschema newJsonschema
      ) null flattened;

      containedIndex = lib.lists.findFirstIndex (
        # newType ⊇ existingType
        # the newType is a superset of an existing type
        # => we need to replace the existing type with the new one
        existingJsonschema: isContainingType newJsonschema existingJsonschema
      ) null flattened;
    in
    if containingIndex != null then
      # Return the same list
      flattened
    else if containedIndex != null then
      clanLib.replaceElemAt flattened containedIndex newJsonschema
    else
      flattened ++ [ newJsonschema ];

  /**
    Checks if t1 is a superset type of t2

    t1 ⊇ t2

    For example to check if a union type can be collapsed.
    This happens in the "either" type

    ```pseudocode
    (str | int) | (str | int)
    =>
    str | int
    ```

    # Examples

    ```nix
    t1 := str | int
    t2 := bool
    isContainingType t1 t2
    => false

    t1 := str | int
    t2 := str
    isContainingType t1 t2
    => true

    t1 := str
    t2 := str | int
    isContainingType t1 t2
    => false

    t1 := str | int
    t2 := str | int
    isContainingType t1 t2
    => true

    t1 := str as readOnly
    t2 := str
    isContainingType t1 t2
    => false
    ```
  */
  isContainingType =
    t1: t2:
    let
      /**
        Checks presence of $attrName in t1 and t2

        Returns a string Enum representing the result of the check

        "bothHave" | "oneHas" | "neitherHas"
      */
      attrStatus =
        attrName:
        if t1 ? ${attrName} then
          if t2 ? ${attrName} then "bothHave" else "oneHas"
        else if t2 ? ${attrName} then
          "oneHas"
        else
          "neitherHas";

      /**
        checks if one attribute name is present in both types and the type of the attribute name is a superset
        or doesnt exist in both types

        Example

        t1 := { foo :: str }
        t2 := { foo :: str | int }
        isContainingAttr "foo"
        => true

        t1 := {  }
        t2 := {  }
        isContainingAttr "foo"
        => true
      */
      isContainingAttr =
        attrName:
        let
          status = attrStatus attrName;
        in
        (status == "bothHave" && isContainingType t1.${attrName} t2.${attrName}) || status == "neitherHas";

      /**
        Checks 'isContainingAttr' for all attributes if the t2.${attrName} is an attribute set.

        t1 := { foo.bar = str | int; }
        t2 := { foo.bar = str | int; ... }
        isContainingAttrs "foo"
        => true

        t1 := { foo.baz = str | int; }
        t2 := { foo.bar = str | int; ... }
        isContainingAttrs "foo"
        => false

        t1 := { foo = { }; }
        t2 := { foo = { }; }
        isContainingAttrs "foo"
        => true

        t1 := { }
        t2 := { }
        isContainingAttrs "foo"
        => true
      */
      isContainingAttrs =
        attrName:
        let
          status = attrStatus attrName;
        in
        status == "bothHave"
        && lib.all (
          name:
          if !(lib.hasAttr name t1.${attrName}) then
            false
          else
            isContainingType t1.${attrName}.${name} t2.${attrName}.${name}
        ) (lib.attrNames t2.${attrName})
        || status == "neitherHas";

      /**
        Check if t2 and t2 contain the same value for the attribute

        Absence of the value is treated as equal value

        t1 := { foo = "str"; }
        t2 := { foo = "str"; ... }
        isSameAttrValue "foo"
        => true

        t1 := { }
        t2 := { }
        isSameAttrValue "foo"
        => true
      */
      isSameAttrValue =
        attrName:
        let
          status = attrStatus attrName;
        in
        status == "bothHave" && t1.${attrName} == t2.${attrName} || status == "neitherHas";

      #
      attrTypeStatus = attrStatus "type";

      #
      attrEnumStatus = attrStatus "enum";

    in
    # cannot merge if only one is readonly
    # t1 := str as readonly
    # t2 := str
    if !isSameAttrValue "readOnly" then
      false
    # Lookup the actual type and call this function again
    # with the resolved type
    else if t1 ? "$ref" then
      isContainingType t1."$ref".jsonschema t2
    # Lookup the actual type and call this function again
    # with the resolved type
    else if t2 ? "$ref" then
      isContainingType t1 t2."$ref".jsonschema

    # Both t1 & t2 are "oneOf"
    # t1 := { oneOf = [ SCHEMA ]; }
    # All of the t2 branches need to be subsets of one of the t1 branches
    else if t1 ? oneOf && t2 ? oneOf then
      lib.all (branch2: lib.any (branch1: isContainingType branch1 branch2) t1.oneOf) t2.oneOf
    # Only t1 is a "oneOf"
    # t1 := { oneOf = [ "str" "int" ]; }
    # t2 := { type = "str"; }
    # t2 needs to be a subset of one of t1 branches
    else if t1 ? oneOf then
      lib.any (branch: isContainingType branch t2) t1.oneOf
    # If both have a type
    # t1 := { type ... }
    # t1 := { type ... }
    else if attrTypeStatus == "bothHave" then
      # Types are not equal
      # hence t1 doesnt contain t2
      if t1.type != t2.type then
        false
      # if t1 := { type = "array"; items = { type = ... }; }
      # t2 must also be array because of the previous if condition
      # the "items" of t2 need to be a subset of t1 "items"
      else if t1.type == "array" then
        isContainingAttr "items" && isContainingAttr "prefixItems"
      # if t1 := { type = "object"; properties = { foo = { type ... } }; }
      # "properties" and "additionalProperties" need to be subset
      # "required" needs to be exactly the same
      else if t1.type == "object" then
        isContainingAttrs "properties"
        && isContainingAttr "additionalProperties"
        && isSameAttrValue "required"
      else
        # If the types are the same
        # And they are not "array" or "object" we treat them as equal
        true
    # If only one t1 or t2 has a "type"
    # they are not subsets
    else if attrTypeStatus == "oneHas" then
      false
    # If both t1 AND t2 are "enum"
    # every element in t2 must be present in t1
    else if attrEnumStatus == "bothHave" then
      lib.all (item: lib.elem item t1.enum) t2.enum
    # only one is an enum
    else if attrEnumStatus == "oneHas" then
      false
    # All other cases
    else
      false;
in
flatten [ ] jsonschemas
