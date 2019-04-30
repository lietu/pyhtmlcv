# pyhtmlcv

Generate HTML CVs from simple (enough) configuration files.

No Word documents, no annoying WYSIWYG editors that leave layout issues
here and there. Just pure JSON and HTML.

Easily extensible template system.

Example configuration is provided in the form of my personal CV.

The configuration format is not exactly self-explanatory however:

- Giving an array to sections -item's "large" field, will convert it's
  contents to an ul -list, making each array item an li
- Adding a plain text string to list of sections, adds a h2 -separator
  on the page
- The contents are NOT HTML encoded when outputting, to make it possible
  to do minor alterations with HTML tags
- Adding the string "-" to list of sections, will add a page break in
  that position. It will not show up in the browser, but when the page
  is printed, it will force a page break there. The styles were created
  so they would also support printing, but some browsers (e.g. Firefox)
  lack proper support for the relevant CSS styles, and guessing is hard,
  so you might need to add these to make it work a bit better.


## Running

Running this tool requires [Python](https://www.python.org/downloads/).

For most common usage you will likely want to run:

```bash
pip install virtualenv
virtualenv .venv
pip install -r requirements.txt
python python pyhtmlcv.py --watch
```

This will install the dependencies in a Python virtualenv and start the
tool watching for any changes you do to the template or source JSON, and
it will generate the site to `generated/cv.json/index.html` whenever it
detects changes.

Add `--help` for more options.

This is however NOT necessary if you use Travis-CI as per suggested use.


## Suggested use

 - Clone / Fork this repository on your own GitHub account
 - Update `cv.json`
 - Go generate a color scheme that suits your needs at
   http://colorschemedesigner.com/ and update
   `templates/default/variables.scss` (or create a whole new template)
 - Confirm that the result is good. Pasting certain special characters
   from Word, for example, can cause issues in the output.
 - Enable [Travis-CI](https://travis-ci.org) for your repository
 - Configure `$GITHUB_TOKEN` for [GitHub pages deployment](https://docs.travis-ci.com/user/deployment/pages/)
