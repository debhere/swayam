# LIC documents

LIC document urls may contain several special characters including some unicode characters. We must replace the special characters before downloading otherwise we may encounter exceptions or downloaded document will not be proper.

## Example 1: Document name is in 'Hindi' or 'Devnagiri Script'

If we encounter something like `जीवन आनंद` in the document name which is clearly not english, we must handle it efficiently.

## Solution

Just add `encoding='utf-8'` in your program if that's not your default setting. I have added utf-8 encoding in my logger so that my logger captures anything corresponds to these characters.

## Example 2: Document name contains characters like :, % etc.

These characters need to be replaced with something like '-' or '_' or '' which makes sense in a file name.

## Solution

```bash
filename = filename.replace(":", "_").replace(")", "")
```
