edi-swim
========

A scraper for the Edinburgh Leisure website which provides a compact list of links to swimming pool timetables.

It does the following:

 - Get www.edinburghleisure.co.uk/venues
 - Pick out the links to any venues which mention swimming
 - Render a page with a list of links to those venue pages
 - Asynchronously fetch each of those pages, parse out the link to the timetable, and update the link in the rendered list.


-- Andrew Davey 2014
