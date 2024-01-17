# API Guidelines

This issue serves to collect our common understanding how to design our API so that it is extensible and usable and understandable.

## Resource oriented

A resource-oriented API is generally modeled as a resource hierarchy, where each node is either a simple resource or a collection resource. For convenience, they are often called a resource and a collection, respectively.

Examples of Resource Nouns:

`machine`
`user`
`flake`

Often resources have sub-resources. Even if it is not foreseen, it is recommended to use plural (trailing `s`) on resources to allow them to be collections of sub-resources.

e.g,

`users`
->
`users/*/profile`

## Verbs

Verbs should not be part of the URL

Bad:
`/api/create-products`

Good:
`/api/products`

Only resources are part of the URL, verbs are described via the HTTP Method.

Exception:

If a different HTTP Method must be used for technical reasons it is okay to terminate the path with a (short) verb / action.

Okay ish:
`/api/products/create`

## Usually the following HTTP Methods exist to interact with a resource

- POST (create an order for a resource)
- GET (retrieve the information)
- PUT (update and replace information)
- PATCH (update and modify information) **(Not used yet)**
- DELETE (delete the item)

## Every resource should be CRUD compatible

All API resources MUST be designed in a way that allows the typical CRUD operations.

Where crud stands for:

C - Create
R - Read
U - Update
D - Delete

Resources should implement at least a "Read" operation.

## Body

Use JSON as an exchange format.

All responses MUST be JSON parseable.

Bad:
`bare string`

Better:
`"quoted string"`

Best: (Enveloped see next section)
`{ name: "quoted string"}`

Errors should have a consistent JSON format, such that it is clear in which field to look at for displaying error messages.

## Envelop all Data collections

Response data should be wrapped into an JSON Object `{}`
Lists `[]` should also contain Objects `{}`.
This allows everything, to be extensible, without breaking backwards compatibility. (Adding fields is trivial, since the schema doesn't change)

Example:

```
{
   "users": [{
     first_name: "John",
     last_name: "Doe",
     …
   }, {
     first_name: "Jane",
     last_name: "Doe",
     …
   }
  ....
  ],
   "skip": 0,
   "limit": 20,
  ....
}
```

Bad Example of a breaking change:
`GET /api/flakes`
`old`

```
[
  "dream2nix"
  "disko"
]
```

`new`

```
[
 {
    name: "dream2nix",
    url: "github/...."
 },
 {
    name: "disko",
    url: "github/...."
 }
]
```

Those kind of breaking changes can be avoided by using an object from the beginning.
Even if the object only contains one key, it is extensible, without breaking.

## More will follow.

...maybe
