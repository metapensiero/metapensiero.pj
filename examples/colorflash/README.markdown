
## Prereqs

* [Django 1.2](http://www.djangoproject.com/)

## Quickstart

In this directory, simply run
<pre>python manage.py runserver</pre>

...and the app should become available at
[http://localhost:8000](http://localhost:8000)

To see the compiled JavaScript:

[http://localhost:8000/static/js/colorflash.js](http://localhost:8000/static/js/colorflash.js)

If you have Closure compiler installed and <code>$CLOSURE_JAR</code> pointing to its .jar, you can see it pretty printed:

[http://localhost:8000/static/js/colorflash.js?mode=pretty](http://localhost:8000/static/js/colorflash.js?mode=pretty)

Or minified:

[http://localhost:8000/static/js/colorflash.js?mode=simple](http://localhost:8000/static/js/colorflash.js?mode=simple)

[http://localhost:8000/static/js/colorflash.js?mode=advanced](http://localhost:8000/static/js/colorflash.js?mode=advanced)