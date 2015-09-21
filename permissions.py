# Copyright (C) 2015 Luke Faraone <luke@faraone.cc>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from time import mktime
from datetime import datetime


class Permission(object):

    """Abstract base class for different functionary roles

    Attributes:
        augroup (str): MediaWiki group name for the group that grants this
            permission. Other groups that may grant this permission will not be
            searched.
        _api (Site): Authenticated Site object for the MediaWiki installation
            for use by subclassses to make queries.

    Args:
        api (Site): Authenticated Site object for the MediaWiki installation
            that will be used to make queries.
    """

    def __init__(self, api):
        self._api = api

    def recent_stamps(self, user, n=5):
        """Returns the last n timestamps of actions by a given user

        Args:
            user (str): Username to query for log actions.
            n (Optional[int]): Number of timestamps to return.

        Returns:
            List[datetime]: A list of `n` or fewer datetime objects.
        """

        stamps = []
        try:
            query = self._logquery(user, limit=n)
            for _ in range(n):
                stamps.append(
                    datetime.fromtimestamp(mktime(
                        query.next()['timestamp']
                    ))
                )
        except StopIteration:
            # Could occur when a user has less than 5 logged actions.
            pass
        return stamps

    def count_actions(self, user, start, stop):
        counter = 0
        for action in self._logquery(user, start=start, stop=stop)
            counter += 1
        return counter


class CheckUser(Permission):
    augroup = "checkuser"

    def _logquery(self, user, start=None, stop=None, **kwargs):
        if start is not None:
            kwargs["to"] = stop
        if stop is not None:
            kwargs["from"] = start

        return self._api.checkuserlog(user, **kwargs)


class Oversight(Permission):
    augroup = "oversight"

    def _logquery(self, user, **kwargs):

        return self._api.logevents(
            "suppress",
            user=user,
            prop=timestamp
            **kwargs
        )
