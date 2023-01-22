RestAPI
=======

OLAF includes an internal REST API using `Flask`_. The REST API is used to give insight into what
the OLAF app is doing during testing and system integration without using the CAN bus.

The REST API provides the ``/od/<index>`` and ``/od/<index>/<subindex>`` endpoints that will
call the internal SDO uploads / downloads, then all other endpoints should be used to render
`Flask templates`_ that can use those two endpoints.

OLAF also include a base template for all other `Flask templates`_ to use. The base templates
includes ``readValue()`` and ``writeValue()`` functions for reading and writing values to the
OD using the index and subindex endpoints, as well as a very basic standarized layout.

.. note:: OLAF will automatically add the core blueprint which includes the ``/od/<index>``
   and ``/od/<index>/<subindex>`` endpoints as well as the all the core templates endpoints.

**Example template that displays a value from the OD**


.. code-block:: html

   <!-- templates/example.html --->

   {% extends 'base.html' %}

   {% block content %}
   <a>Data: <span id='data'></span></a>
   <script>
     /** Update the data value */
     async function updateData() {
      const obj = await readValue('0x6000', '0x01');
      document.getElementById('data').textContent = obj.value;
     }

     // update data initially and every 30s after that
     updateData();
     const interval = setInterval(function() {
       updateData();
     }, 30000);
   </script>
   {% endblock %}


.. code-block:: python

   # main.py

   from flask import Blueprint, render_template
   from olaf import rest_api, olaf_run

   example_bp = Blueprint('example_template', __name__, template_folder='templates')


   @example_bp.route('/example')
   def example_template():
       return render_template('example.html', title=os.uname()[1], name='Example')


   def main():
       rest_api.add_blueprint(example_bp)
       olaf_run('app.dcf')


   if __name__ == '__main__':
       main()


.. autoclass:: olaf._internals.rest_api.RestAPI
   :class-doc-from: both
   :members:
   :member-order: bysource

.. _Flask: https://github.com/pallets/flask
.. _Flask templates: https://flask.palletsprojects.com/en/latest/tutorial/templates/
