.. django-model-values documentation master file, created by sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-model-values's documentation.
===============================================
Taking the **O** out of **ORM**.

Introduction
^^^^^^^^^^^^
Provides `Django`_ model utilities for encouraging direct data access instead of unnecessary object overhead.
Implemented through compatible method and operator extensions [#compat]_ to `QuerySets <reference.html#queryset>`_ and `Managers <reference.html#manager>`_.

The primary motivation is the experiential observation that the active record pattern - specifically ``Model.save`` - is the root of all evil.
The secondary goal is to provide a more intuitive data layer, similar to PyData projects such as `pandas`_.

Usage:  instantiate the `custom manager`_ in your models.

Updates
^^^^^^^^^^^^
*The Bad*::

   book = Book.objects.get(pk=pk)
   book.rating = 5.0
   book.save()

This example is ubiquitous and even encouraged in many django circles.  It's also an epic fail.

   * Runs an unnecessary select query, as no fields need to be read.
   * Updates all fields instead of just the one needed.
   * Therefore also suffers from race conditions.
   * And is relatively verbose, without addressing errors yet.

The solution is relatively well-known, and endorsed by `django's own docs`_, but remains under-utilized.

*The Ugly*::

   Book.objects.filter(pk=pk).update(rating=5.0)

So why not provide syntactic support for the better approach.
The `Manager <reference.html#manager>`_ supports filtering by primary key, since that's so common.
The `QuerySet <reference.html#queryset>`_ supports column updates.

*The Good*::

   Book.objects[pk]['rating'] = 5.0

But one might posit...

   * "Isn't the encapsulation ``save`` provides worth it in principle?"
   * "Doesn't the new ``update_fields`` option fix this in practice?"
   * "What if the object is cached or has custom logic in the ``save`` method?"

No, no, and good luck with that. [#dogma]_  Consider a more realistic example which addresses these concerns.

*The Bad*::

   try:
      book = Book.objects.get(pk=pk)
   except Book.DoesNotExist:
      changed = False
   else:
      changed = book.publisher != publisher
      if changed:
         book.publisher = publisher
         book.pubdate = today
         book.save(update_fields=['publisher', 'pubdate'])

This solves the most severe problem, though with more verbosity and still an unnecessary read. [#preopt]_
Note handling ``pubdate`` in the ``save`` implementation would only spare the caller one line of code.
But the real problem is how to handle custom logic when ``update_fields`` *isn't* specificed.
There's no one obvious correct behavior, which is why projects like `django-model-utils`_ have to track the changes on the object itself. [#OO]_

A better approach would be an ``update_publisher`` method which does all and only what is required.
So what would such an implementation be?  A straight-forward update won't work, yet only a minor tweak is needed.

*The Ugly*::

   changed = Book.objects.filter(pk=pk).exclude(publisher=publisher) \ 
      .update(publisher=publisher, pubdate=today)

Now the update is only executed if necessary.
And this can be generalized with a little inspiration from ``{get,update}_or_create``.

*The Good*::

   changed = Book.objects[pk].change({'pubdate': today}, publisher=publisher)

Selects
^^^^^^^^^^^^
Direct column access has some of the clunkiest syntax:  ``values_list(..., flat=True)``.
`QuerySets <reference.html#queryset>`_  override ``__getitem__``, as well as comparison operators for simple filters.
Both are common syntax in panel data layers.

*The Bad*::

   {book.pk: book.name for book in qs}

   (book.name for book in qs.filter(name__isnull=False))

   if qs.filter(author=author):

*The Ugly*::

   dict(qs.values_list('pk', 'name'))

   qs.exclude(name=None).values_list('name', flat=True)

   if qs.filter(author=author).exists():

*The Good*::

   dict(qs['pk', 'name'])

   qs['name'] != None

   if author in qs['author']:

Aggregation
^^^^^^^^^^^^
Once accustomed to working with data values, a richer set of aggregations becomes possible.
Again the method names mirror projects like `pandas`_ whenever applicable.

*The Bad*::

   collections.Counter(book.author for book in qs)

   sum(book.rating for book in qs) / len(qs)

   counts = collections.Counter()
   for book in qs:
      counts[book.author] += book.quantity

*The Ugly*::

   dict(qs.values_list('author').annotate(model.Count('author')))

   qs.aggregate(models.Avg('rating'))['rating__avg']

   dict(qs.values_list('author').annotate(models.Sum('quantity')))

*The Good*::

   dict(qs['author'].value_counts())

   qs['rating'].mean()

   dict(qs['quantity'].groupby('author').sum())

Expressions
^^^^^^^^^^^^
``F`` expressions are similarly extended to easily create ``Q``, ``Func``, and ``OrderBy`` objects.
Note they can be used directly even without a custom manager.

*The Bad*::

   (book for book in qs if book.author.startswith('A') or book.author.startswith('B'))

   (book.title[:10] for book in qs)

   for book in qs:
      book.rating += 1
      book.save()

*The Ugly*::

   qs.filter(Q(author__startswith='A') | Q(author__startswith='B'))

   qs.values_list(functions.Substr('title', 1, 10), flat=True)

   qs.update(rating=models.F('rating') + 1)

*The Good*::

   qs[F.any(map(F.author.startswith, 'AB'))]

   qs[F.title[:10]]

   qs['rating'] += 1

Conditionals
^^^^^^^^^^^^
Annotations and updates with ``Case`` and ``When`` expressions.
See also `bulk_changed and bulk_change <reference.html#manager>`_ for efficient bulk operations on primary keys.

*The Bad*::

   collections.Counter('low' if book.quantity < 10 else 'high' for book in qs).items()

   for author, quantity in items:
      for book in qs.filter(author=author):
         book.quantity = quantity
         book.save()

*The Ugly*::

   qs.values_list(models.Case(
      models.When(quantity__lt=10, then=models.Value('low')),
      models.When(quantity__gte=10, then=models.Value('high')),
      output_field=models.CharField(),
   )).annotate(count=models.Count('*'))

   cases = (models.When(author=author, then=models.Value(quantity)) for author, quantity in items)
   qs.update(quantity=models.Case(*cases, default='quantity'))

*The Good*::

   qs[{F.quantity < 10: 'low', F.quantity >= 10: 'high'}].value_counts()

   qs['quantity'] = {F.author == author: quantity for author, quantity in items}

Contents
==================
.. toctree::
   :maxdepth: 1

   reference
   example

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _django: https://docs.djangoproject.com
.. _pandas: http://pandas.pydata.org
.. _`custom manager`: https://docs.djangoproject.com/en/stable/topics/db/managers/#custom-managers
.. _`django's own docs`: https://docs.djangoproject.com/en/stable/ref/models/querysets/#update
.. _`django-model-utils`: https://pypi.org/project/django-model-utils/

.. rubric:: Footnotes

.. [#compat] The only incompatible changes are edge cases which aren't documented behavior, such as queryset comparison.
.. [#dogma] In the *vast* majority of instances of that idiom, the object is immediately discarded and no custom logic is necessary.
   Furthermore the dogma of a model knowing how to serialize itself doesn't inherently imply a single all-purpose instance method.
   Specialized classmethods or manager methods would be just as encapsulated.
.. [#preopt] Premature optimization?  While debatable with respect to general object overhead, nothing good can come from running superfluous database queries.
.. [#OO] Supporting ``update_fields`` with custom logic also results in complex conditionals, ironic given that OO methodology ostensibly favors separate methods over large switch statements.
