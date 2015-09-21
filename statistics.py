#!/usr/bin/env python
#
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


from __future__ import print_function

import argparse
import logging
import sys

from datetime import datetime, timedelta

import yaml

from mwclient import Site
from tabulate import tabulate
from babel.dates import format_timedelta

from permissions import CheckUser, Oversight

USER_AGENT = "AUSCReport/0.1 b.t.y.b. LFaraone@enwiki"

DEFAULT_API_ROOT = "en.wikipedia.org/w/api.php"

root_logger = logging.getLogger(__name__)
root_logger.addHandler(logging.NullHandler())


def exempt_users(conffile="excuses.yaml"):
    """Parse list of users who are exempt from activity requirements"""

    with open(conffile) as fp:
        conf = yaml.safe_load(fp)

    exemptions_by_user = {}
    for role, users in conf.iteritems():
        for user in users:
            exemptions_by_user[user] = role

    return exemptions_by_user


def latest_statistics(
        api,
        permissions,
        # TODO(lfaraone): add back delta, maybe?
        mw_tables=False,
        stream=sys.stdout,
):
    """Generates and prints to stdout a report of inactive users

    Args:
        api (Site): Authenticated Site object for the MediaWiki installation
            that will be used to make queries.
        permissions (List(Permission)): List of permission classes (not
            objects) to check against.
        mw_tables (bool): Whether to use MediaWiki formatting in output.
        stream (Optional(file)): File object to which report output will be
            written.
    """

    log = root_logger.getChild("activity_report")

    if mw_tables:
        tablefmt = "mediawiki"
    else:
        tablefmt = "simple" 

    now = datetime.now()
    # TODO(lfaraone): this is totally the wrong number
    activity_cutoff = now - timedelta(days=30)
    timing = {
        "start": str(now),
        "stop": str(activity_cutoff),
    }

    # XXX The rest of this file below this line hasn't been converted

    report = []
    # Iterate through the various roles to check.
    for role_class in permissions:
        role = role_class(api)

        # Log entries in this loop should be annotated with the group we're
        # acting on.
        log, log_ = log.getChild(role.augroup), log

        candidates = api.allusers(group=role.augroup)

        actions_by_user = {
            e['name']: role.count_actions(e['name'], *timing) for e in candidates
        }

        log.debug("Retrieved actions for %i users",
                  len(actions_by_user.keys()), role.augroup)

        inactive = []


        # Iterate through users and the timestamps of their latest actions to
        # determine whether they're past the current threshold for activity.
        for user, timestamps in actions_by_user.iteritems():
            log.debug("Found %i timestamps for %s; last timestamp is %s",
                      len(timestamps),
                      user,
                      timestamps[-1] if len(timestamps) else "n/a",
                      )
            # If we don't have any actions at all, bail before doing an
            # out-of-bounds access.
            if len(timestamps) and timestamps[-1] >= activity_cutoff:
                recently_active.append(user)
                log.debug("Marking %s as active", user)
            else:
                log.debug("Marking %s as inactive", user)
                inactive.append((user, timestamps))

        report.append((role.augroup, inactive))

        # Reset the logger to its previous value
        log = log_

    exemptions = exempt_users()

    headers = (
        "User",
        "<%id" % cutoff_delta.days,
        "Last action",
        "Exemption",
    )

    for permission, inactives in report:
        # All output goes to the `stream` parameter
        print(permission, "inactivity report", file=stream)
        print(tabulate(
            # Do a list comprehension to generate tabular data for each user
            # that has been recently inactive.
            [
                (
                    # Username
                    user,
                    # Number of recent actions
                    len([a for a in actions if a >= activity_cutoff]),
                    # Relative time from now since last action
                    (
                        format_timedelta(now - actions[0])
                        if len(actions) else "None"
                    ),
                    # Any activity requirement exemptions the user possesses
                    exemptions.get(user, ""),
                ) for user, actions in inactives
            ],
            headers=headers,
            tablefmt=tablefmt,
        ), file=stream)
        # Newline between reports
        print(file=stream)


def days_to_timedelta(arg):
    try:
        return timedelta(days=int(arg))
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Invalid delta days specified to --cutoff-time")


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Generate an inactivity report for functionaries")

    parser.add_argument(
        "-d", "--debug", action="store_true",
        help="Enable debug logging")
    parser.add_argument(
        "--api-root", type=str, default=DEFAULT_API_ROOT,
        help="API root to query")
    parser.add_argument(
        "--mw-table", action="store_true",
        help="Output tables in MediaWiki format")
    parser.add_argument(
        "--cutoff", type=days_to_timedelta, default="90", metavar="DAYS",
        help="Number of days to use as a cutoff for inactivity")

    return parser


def main(args=None):
    if args is None:
        parser = setup_parser()
        args = parser.parse_args()

    # Configure logging to console, optionally including debug-level logs

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)

    root_logger.addHandler(console_handler)

    username = raw_input("Username: ").strip()
    password = raw_input("Password: ").strip()

    # Log in
    api = Site(("https", args.api_root), clients_useragent=USER_AGENT)
    api.login(username, password)

    activity_report(api, (CheckUser, Oversight), args.cutoff, mw_tables=args.mw_table)
