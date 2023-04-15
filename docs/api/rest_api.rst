Rest API
========

OLAF includes an internal REST API using `Flask`_. The REST API is used to give insight into what
the OLAF app is doing during testing and system integration without using the CAN bus.

The REST API provides the ``/od/<index>`` and ``/od/<index>/<subindex>`` endpoints that will
call the internal SDO uploads / downloads, then all other endpoints should be used to render
`Flask templates`_ that can use those two endpoints.

OLAF also include a base template for all other `Flask templates`_ to use. The base templates
includes ``readValue()`` and ``writeValue()`` functions for reading and writing values to the
OD using the index and subindex endpoints, the ``scetToDate()`` function for convert SCET
values to the native JavaScript ``Date`` object, as well as a very basic standarized layout.

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

   from olaf import rest_api, olaf_run
   from olaf import olaf_setup, olaf_run, app, rest_api, render_olaf_template

   @rest_api.app.route('/example')
   def example_template():
       return render_olaf_template('example.html', name='Example')

   def main():
       path = os.path.dirname(os.path.abspath(__file__))
       args = olaf_setup(f'{path}/app.dcf')  # path to eds or dcf file

       rest_api.add_template(f'{path}/templates/example.html')  # path to Flask template

       olaf_run()


   if __name__ == '__main__':
       main()


.. autoclass:: olaf.RestAPI
   :class-doc-from: both
   :members:
   :member-order: bysource

.. autofunction:: olaf.render_olaf_template

.. _Flask: https://github.com/pallets/flask
.. _Flask templates: https://flask.palletsprojects.com/en/latest/tutorial/templates/
