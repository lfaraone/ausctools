ausctools
=========

Tools for generating reports for functionary activity on Wikipedia and related projects.

Usage
----------

Install via the standard ``python setup.py install``. To generate an report for the English Wikipedia listing users who have been inactive in the past 90 days::

    functionaries-activity-report --api-root en.wikipedia.org/w/api.php --cutoff 90

You will need the credentials of a user with ``checkuser-log`` and ``suppressionlog`` on the relevant MediaWiki installation.

Sponsors
--------
.. image:: assets/sponsors/termius-icon.svg
  :width: 400
  :alt: Logo of Termius
[Termius][1] provides a secure, reliable, and collaborative SSH client.

[1]: https://termius.com/