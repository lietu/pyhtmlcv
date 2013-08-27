pyhtmlcv
========

Generates HTML CVs from a JSON configuration with Python using Jinja2 templates. These templates can be extended easily to create themes.

Example configuration is provided in the form of my personal CV, can be found in the file lietu.json.

The configuration has a couple of special cases that are not completely obvious:
* Giving an array to sections -item's "large" field, will convert it's contents to an ul -list, making each array item an li
* Adding a plain text string to list of sections, adds a h2 -separator on the page
* The contents are NOT HTML encoded when outputting, to make it possible to do minor alterations with HTML tags
* Adding the string "-" to list of sections, will add a page break in that position. It will not show up in the browser, but when the page is printed, it will force a page break there. The styles were created so they would also support printing, but some browsers (e.g. Firefox) lack proper support for the relevant CSS styles and you will need to add these to make it work a bit better.



Suggested use
=============

 * Copy lietu.json to yourname.json, fill in your own information and customize to taste.
 * Go generate a color scheme that suits your needs at http://colorschemedesigner.com/ and update teamplates/variables.less accordingly.
 * Generate the HTML by running "python pyhtmlcv.py yourname.json"
 * Confirm that the result is good. Pasting certain special characters from Word, for example, can cause issues in the output. Also, Google Chrome will refuse to work with the client-side LESS parser if you are trying to access the HTML file over file:// protocol, some other browsers might also.
 * Install Node.js and the LESS compiler (npm package is called less), and run "lessc templates/style.less style.css", copy the style.css with your HTML CV
 * Remove the script -tag for the LESS parser from the HTML CV, and change the link tag to <link rel="stylesheet" type="text/css" href="style.css">
 * Rename generated .html file to "cv.html", and publish generated/yourname
 .json/* on
 the web

