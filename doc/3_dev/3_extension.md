### *ApexHDL Documentation*
# 3.3. Framework extension

## 3.3.1. Parameter addition

- All you have to do is **adding a new field** in the `apex.Context` class, following the pattern:
```python
    parameter_name: <param-type> = field(metadata={
        "description": "<param-description>",
        "group": "<param-group>",
        "allow_multiple": <param-multiple-bool>
    })
    """<param-description>"""
```
- Since ApexHDL is engineered to **dynamically deal with the parameters** put in the `Context`, your new parameter will automatically be:
    - Added in the user **arguments parser**,
    - Added in the **console manual**,
    - And **ready to use** throughout your code!

## 3.3.2. Variant addition

- All you have to do is **adding a new file** in the `apex.*_stage.variants`, following the pattern:
```python
@<Stage>Registry.register(predicate=<predicate>, priority=<priority>)
class <Stage><VariantName>(<Stage>Stage):
    """
    <Variant-documentation>
    """
    
    def execute(self, ctx: Context) -> dict[str, float]:
        (...)
```
- In this pattern, you shall replace:
    - `<Stage>` with the name of the stage of your variant,
    - `<VariantName>` with the unique name of your variant, with its documentation `<Variant-documentation>`,
    - `<predicate>` with a function on the `Context` instance (named `ctx`), returning a boolean (you may use `lambda` function for clarity),
    - `<priority>` with a priority integer, knowing that higher priorities are evaluated first (you may look at priorities of other variants of the stage beforehand).
- In the Python algorithm of your variant:
    - if you want to use external executables, you may think about **using `subprocess`** Python capabilities (documented [here](https://docs.python.org/3/library/subprocess.html)),
    - if you want to use external scripts (namely Tcl, XDC, ...), you may think about putting in the right place in the **ApexHDL codebase** (namely in existing `tcl/`, `xdc/`, ... or in a new folder).
