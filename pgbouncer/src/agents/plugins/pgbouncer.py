#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Checkmk GmbH & 2024 Mayr Stefan
# License: GNU General Public License v2
# This file is derived from mk_postgres which is part of Checkmk (https://checkmk.com).
# It is subject to the terms and conditions defined in the file COPYING, which is part
# of this source code package of Checkmk.
r"""Check_MK Agent Plugin: pgbouncer

This is a Check_MK Agent plugin. If configured, it will be called by the
agent without any arguments.

Can be configured with $MK_CONFDIR/pgbouncer.cfg
Example for pgbouncer.cfg file:

-----pgbouncer.cfg----------------------------------------
DBUSER=postgres
PG_BINARY_PATH=/usr/bin/psql
INSTANCE=/home/postgres/db1.env:USER_NAME:/PATH/TO/.pgpass:
INSTANCE=/home/postgres/db2.env:USER_NAME:/PATH/TO/.pgpass:INSTANCE_NAME
----------------------------------------------------------

Example of an environment file:

-----/home/postgres/db1.env-----------------------------------------
export PGDATABASE="pgbouncer"
export PGPORT="6432"
export PGVERSION="14"
----------------------------------------------------------

Inside of the environment file, only `PGPORT` is mandatory.
If an `INSTANCE` is specified without an `INSTANCE_NAME` the port before the dot is used as
the `INSTANCE_NAME`.
For example:

INSTANCE=/home/postgres/db1.env:USER_NAME:/PATH/TO/.pgpass:

will use db1 as `INSTANCE_NAME`.

In case there is no `INSTANCE` specified by the pgbouncer.cfg, then the plugin assumes defaults.
For example, the configuration

-----pgbouncer.cfg----------------------------------------
DBUSER=postgres
PG_BINARY_PATH=/usr/bin/psql
----------------------------------------------------------

is equivalent to

-----pgbouncer.cfg----------------------------------------
DBUSER=postgres
PG_BINARY_PATH=/usr/bin/psql
INSTANCE=/home/postgres/does-not-exist.env:postgres::default
----------------------------------------------------------

-----/home/postgres/does-not-exist.env--------------------
export PGDATABASE="pgbouncer"
export PGPORT="6432"
----------------------------------------------------------

The only difference being `/home/postgres/does-not-exist.env` does not exist in the first setup.
Different defaults are chosen for Windows.
"""

__version__ = "2.2.0b21"

import abc
import io
import logging

# optparse exist in python2.6 up to python 3.8. Do not use argparse, because it will not run with python2.6
import optparse  # pylint: disable=W0402
import os
import platform
import re
import subprocess
import sys

try:
    from collections.abc import (  # noqa: F401 # pylint: disable=unused-import
        Callable,
        Iterable,
        Sequence,
    )
    from typing import Any  # noqa: F401 # pylint: disable=unused-import
except ImportError:
    # We need typing only for testing
    pass

# For Python 3 sys.stdout creates \r\n as newline for Windows.
# Checkmk can't handle this therefore we rewrite sys.stdout to a new_stdout function.
# If you want to use the old behaviour just use old_stdout.
if sys.version_info[0] >= 3:
    new_stdout = io.TextIOWrapper(
        sys.stdout.buffer, newline="\n", encoding=sys.stdout.encoding, errors=sys.stdout.errors
    )
    old_stdout, sys.stdout = sys.stdout, new_stdout

OS = platform.system()
IS_LINUX = OS == "Linux"
IS_WINDOWS = OS == "Windows"
LOGGER = logging.getLogger(__name__)

if sys.version_info[0] >= 3:
    UTF_8_NEWLINE_CHARS = re.compile(r"[\n\r\u2028\u000B\u0085\u2028\u2029]+")
else:
    UTF_8_NEWLINE_CHARS = re.compile("[\u000A\u000D\u2028\u000B\u0085\u2028\u2029]+")  # fmt: skip


class OSNotImplementedError(NotImplementedError):
    def __str__(self):
        # type: () -> str
        return "The OS type ({}) is not yet implemented.".format(platform.system())


if IS_LINUX:
    import resource
elif IS_WINDOWS:
    import time
else:
    raise OSNotImplementedError


# for compatibility with python 2.6
def subprocess_check_output(args):
    return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]


# Borrowed from six
def ensure_str(s):
    if sys.version_info[0] >= 3:
        if isinstance(s, bytes):
            return s.decode("utf-8")
    else:
        if isinstance(s, unicode):  # pylint: disable=undefined-variable
            return s.encode("utf-8")
    return s


class PgbouncerPsqlError(RuntimeError):
    pass


class PgbouncerBase:
    """
    Base class for x-plattform postgres queries
    :param db_user: The postgres db user
    :param instance: Pass an instance, in case of monitoring a server with multiple instances

    All abstract methods must have individual implementation depending on the OS type
    which runs postgres.
    All non-abstract methods are meant to work on all OS types which were subclassed.
    """

    __metaclass__ = abc.ABCMeta
    _supported_pg_versions = ["12"]

    def __init__(self, db_user, pg_binary_path, instance):
        # type: (str, str | None, dict, Sequence[re.Pattern]) -> None
        self.db_user = db_user
        self.name = instance["name"]
        self.pg_user = instance["pg_user"]
        self.pg_host = instance["pg_host"]
        self.pg_port = instance["pg_port"]
        self.pg_database = instance["pg_database"]
        self.pg_passfile = instance.get("pg_passfile", "")
        self.pg_version = instance.get("pg_version")
        self.my_env = os.environ.copy()
        self.my_env["PGPASSFILE"] = instance.get("pg_passfile", "")
        self.psql_binary_name = "psql"
        if pg_binary_path is None:
            self.psql_binary_path = self.get_psql_binary_path()
        else:
            self.psql_binary_path = pg_binary_path
        self.psql_binary_dirname = self.get_psql_binary_dirname()
        self.conn_time = ""  # For caching as conn_time and version are in one query

    @abc.abstractmethod
    def run_sql_as_db_user(
        self, sql_cmd, extra_args="", field_sep=";", quiet=True, rows_only=True, mixed_cmd=False
    ):
        # type: (str, str, str, bool, bool, bool) -> str
        """This method implements the system specific way to call the psql interface"""

    @abc.abstractmethod
    def get_psql_binary_path(self):
        """This method returns the system specific psql binary and its path"""

    @abc.abstractmethod
    def get_psql_binary_dirname(self):
        """This method returns the system specific psql binary and its path"""

    @abc.abstractmethod
    def get_instances(self):
        """Gets all instances"""

    @abc.abstractmethod
    def get_version_and_connection_time(self):
        """Get the pgbouncer version and the time for the query connection"""

    def get_server_version(self):
        """Gets the server version"""
        out = self.run_sql_as_db_user("SHOW VERSION;")
        if out == "":
            raise PgbouncerPsqlError("psql connection returned with no data")
        version_as_string = out.split()[1]
        return version_as_string

    def get_condition_vars(self, numeric_version): # pylint: disable=unused-argument
        """Gets condition variables for other queries"""
        #if numeric_version > 9.2:
        #    return "state", "'idle'"
        return "current_query", "'<IDLE>'"

    def get_clients(self):
        """Gets all client connections"""
        sql_cmd = (
            "SHOW CLIENTS;"
        )

        out = self.run_sql_as_db_user(
            sql_cmd, rows_only=False, extra_args="-P footer=off"
        )

        return out

    def get_pools(self):
        """Gets all backend pools"""
        sql_cmd = (
            "SHOW POOLS;"
        )

        out = self.run_sql_as_db_user(
            sql_cmd, rows_only=False, extra_args="-P footer=off"
        )

        return out

    def get_databases(self):
        """Gets all databases"""
        sql_cmd = (
            "SHOW DATABASES;"
        )

        out = self.run_sql_as_db_user(
            sql_cmd, rows_only=False, extra_args="-P footer=off"
        )

        return out

    def get_limits(self):
        """Gets configuration limits (max_*)"""
        sql_cmd = (
            "SHOW CONFIG;"
        )

        out = self.run_sql_as_db_user(
            sql_cmd, rows_only=True, extra_args="-P footer=off"
        )

        return "\n".join([
            line
            for line in out.splitlines()
            if line.startswith("max_")
        ])

    def get_version(self):
        """Wrapper around get_version_conn_time"""
        version, self.conn_time = self.get_version_and_connection_time()
        return version

    def get_connection_time(self):
        """
        Wrapper around get_version_conn time.
        Execute query only if conn_time wasn't already set
        """
        if self.conn_time == "":
            _, self.conn_time = self.get_version_and_connection_time()
        return self.conn_time

    def is_pg_ready(self):
        """Executes pg_isready.
        pg_isready is a utility for checking the connection status of a PostgreSQL database server.
        """

        out = subprocess_check_output(
            ["%s%spg_isready" % (self.psql_binary_dirname, os.sep), "-p", self.pg_port],
        )

        sys.stdout.write("%s\n" % ensure_str(out))

    def execute_all_queries(self):
        """Executes all queries and writes the output formatted to stdout"""
        instance = "\n[[[%s]]]" % self.name

        try:
            databases = self.get_databases()
            database_text = "\n[databases_start]\n%s\n[databases_end]" % "\n".join(databases)
            version = self.get_server_version()
            row, idle = self.get_condition_vars(version)
        except PgbouncerPsqlError:
            # if tcp connection to db instance failed variables are empty
            databases = ""
            database_text = ""
            version = None
            row, idle = "", ""

        out = "<<<pgbouncer_instances>>>"
        out += instance
        sys.stdout.write("%s\n" % out)

        out = "<<<pgbouncer_clients:sep(59)>>>"
        out += instance
        out += "\n%s" % self.get_clients()
        sys.stdout.write("%s\n" % out)

        out = "<<<pgbouncer_pools:sep(59)>>>"
        out += instance
        out += "\n%s" % self.get_pools()
        sys.stdout.write("%s\n" % out)

        out = "<<<pgbouncer_databases:sep(59)>>>"
        out += instance
        out += "\n%s" % self.get_databases()
        sys.stdout.write("%s\n" % out)

        out = "<<<pgbouncer_limits>>>"
        out += instance
        out += "\n%s" % self.get_limits()
        sys.stdout.write("%s\n" % out)

        out = "<<<pgbouncer_version:sep(1)>>>"
        out += instance
        out += "\n%s" % self.get_version()
        sys.stdout.write("%s\n" % out)

        out = "<<<pgbouncer_conn_time>>>"
        out += instance
        out += "\n%s" % self.get_connection_time()
        sys.stdout.write("%s\n" % out)

def _sanitize_sql_query(out):
    # type: (bytes) -> str
    utf_8_out = ensure_str(out)
    # The sql queries may contain any char in `UTF_8_NEWLINE_CHARS`. However,
    # Checkmk only knows how to handle `\n`. Furthermore, `\n` is always
    # interpreted as a record break by Checkmk (see `parse_dbs`). This means
    # that we have to remove all newline chars, before printing the section. We
    # solve the issue in three steps.
    # - Make Pgbouncer return the NULL byte (instead of newlines). This achieved
    #   by using the flag `-0`.
    # - Remove all newlines from whatever Pgbouncer returns. This is safe,
    #   because of the first step.
    # - Finally, turn the NULL bytes into linebreaks, so Checkmk interprets
    #   them as record breaks.
    utf_8_out_no_new_lines = UTF_8_NEWLINE_CHARS.sub(" ", utf_8_out)
    return utf_8_out_no_new_lines.replace("\x00", "\n").rstrip()


class PgbouncerWin(PgbouncerBase):
    def run_sql_as_db_user(
        self, sql_cmd, extra_args="", field_sep=";", quiet=True, rows_only=True, mixed_cmd=False
    ):
        # type: (str, str, str, bool | None, bool | None,bool | None) -> str
        """This method implements the system specific way to call the psql interface"""
        extra_args += " -U %s" % self.pg_user
        extra_args += " -d %s" % self.pg_database
        extra_args += " -h %s" % self.pg_host
        extra_args += " -p %s" % self.pg_port

        if quiet:
            extra_args += " -q"
        if rows_only:
            extra_args += " -t"

        if mixed_cmd:
            cmd_str = 'cmd /c echo %s | cmd /c ""%s" -X %s -A -0 -F"%s" -U %s"' % (
                sql_cmd,
                self.psql_binary_path,
                extra_args,
                field_sep,
                self.db_user,
            )

        else:
            cmd_str = 'cmd /c ""%s" -X %s -A -0 -F"%s" -U %s -c "%s"" ' % (
                self.psql_binary_path,
                extra_args,
                field_sep,
                self.db_user,
                sql_cmd,
            )
        proc = subprocess.Popen(  # pylint: disable=consider-using-with
            cmd_str,
            env=self.my_env,
            stdout=subprocess.PIPE,
        )
        out = proc.communicate()[0]
        return _sanitize_sql_query(out)

    @staticmethod
    def _call_wmic_logicaldisk():
        # type: () -> str
        return ensure_str(
            subprocess_check_output(
                [
                    "wmic",
                    "logicaldisk",
                    "get",
                    "deviceid",
                ]
            )
        )

    @staticmethod
    def _parse_wmic_logicaldisk(wmic_output):
        # type: (str) -> Iterable[str]
        for drive in wmic_output.replace("DeviceID", "").split(":")[:-1]:
            yield drive.strip()

    @classmethod
    def _logical_drives(cls):
        # type: () -> Iterable[str]
        yield from cls._parse_wmic_logicaldisk(cls._call_wmic_logicaldisk())

    def get_psql_binary_path(self):
        # type: () -> str
        """This method returns the system specific psql interface binary as callable string"""
        if self.pg_version is None:
            # This is a fallback in case the user does not have any instances
            # configured.
            return self._default_psql_binary_path()
        return self._psql_path(self.pg_version)

    def _default_psql_binary_path(self):
        # type: () -> str
        for pg_version in self._supported_pg_versions:
            try:
                return self._psql_path(pg_version)
            except IOError as e:
                ioerr = e
                continue
        raise ioerr

    def _psql_path(self, pg_version):
        # type: (str) -> str

        # TODO: Make this more clever...
        for drive in self._logical_drives():
            for program_path in [
                "Program Files\\PostgreSQL",
                "Program Files (x86)\\PostgreSQL",
                "PostgreSQL",
            ]:
                psql_path = (
                    "{drive}:\\{program_path}\\{pg_version}\\bin\\{psql_binary_name}.exe".format(
                        drive=drive,
                        program_path=program_path,
                        pg_version=pg_version.split(".", 1)[
                            0
                        ],  # Only the major version is relevant
                        psql_binary_name=self.psql_binary_name,
                    )
                )
                if os.path.isfile(psql_path):
                    return psql_path

        raise IOError("Could not determine %s bin and its path." % self.psql_binary_name)

    def get_psql_binary_dirname(self):
        # type: () -> str
        return self.psql_binary_path.rsplit("\\", 1)[0]

    def get_version_and_connection_time(self):
        # type: () -> tuple[str, str]
        """Get the pgbouncer version and the time for the query connection"""

        # TODO: Verify this time measurement
        start_time = time.time() # pylint: disable=possibly-used-before-assignment
        out = self.get_server_version()
        diff = time.time() - start_time
        return out, "%.3f" % diff


class PgbouncerLinux(PgbouncerBase):
    def run_sql_as_db_user(
        self, sql_cmd, extra_args="", field_sep=";", quiet=True, rows_only=True, mixed_cmd=False
    ):
        # type: (str, str, str, bool, bool, bool) -> str
        base_cmd_list = ["su", "-", self.db_user, "-c", r"""PGPASSFILE=%s %s -X %s -A0 -F'%s'%s"""]
        extra_args += " -U %s" % self.pg_user
        extra_args += " -d %s" % self.pg_database
        extra_args += " -h %s" % self.pg_host
        extra_args += " -p %s" % self.pg_port

        if quiet:
            extra_args += " -q"
        if rows_only:
            extra_args += " -t"

        # In case we want to use postgres meta commands AND SQL queries in one call, we need to pipe
        # the full cmd string into psql executable
        # see https://www.postgresql.org/docs/9.2/app-psql.html
        if mixed_cmd:
            cmd_to_pipe = subprocess.Popen(  # pylint: disable=consider-using-with
                ["echo", sql_cmd], stdout=subprocess.PIPE
            )
            base_cmd_list[-1] = base_cmd_list[-1] % (
                self.pg_passfile,
                self.psql_binary_path,
                extra_args,
                field_sep,
                "",
            )

            receiving_pipe = subprocess.Popen(  # pylint: disable=consider-using-with
                base_cmd_list, stdin=cmd_to_pipe.stdout, stdout=subprocess.PIPE, env=self.my_env
            )
            out = receiving_pipe.communicate()[0]

        else:
            base_cmd_list[-1] = base_cmd_list[-1] % (
                self.pg_passfile,
                self.psql_binary_path,
                extra_args,
                field_sep,
                ' -c "%s" ' % sql_cmd,
            )
            proc = subprocess.Popen(  # pylint: disable=consider-using-with
                base_cmd_list, env=self.my_env, stdout=subprocess.PIPE
            )
            out = proc.communicate()[0]

        return _sanitize_sql_query(out)

    def get_psql_binary_path(self):
        # type: () -> str
        """If possible, do not use the binary from PATH directly. This could lead to a generic
        binary that is not able to find the correct UNIX socket. See SUP-11729.
        In case the user does not have any instances configured or if the assembled path does not
        exist, fallback to the PATH location. See SUP-12878"""

        if self.pg_version is None:
            return self._default_psql_binary_path()

        binary_path = "/{pg_database}/{pg_version}/bin/{psql_binary_name}".format(
            pg_database=self.pg_database,
            pg_version=self.pg_version,
            psql_binary_name=self.psql_binary_name,
        )

        if not os.path.isfile(binary_path):
            return self._default_psql_binary_path()
        return binary_path

    def _default_psql_binary_path(self):
        # type: () -> str
        proc = subprocess.Popen(  # pylint: disable=consider-using-with
            ["which", self.psql_binary_name], stdout=subprocess.PIPE
        )
        out = ensure_str(proc.communicate()[0])

        if proc.returncode != 0:
            raise RuntimeError("Could not determine %s executable." % self.psql_binary_name)

        return out.strip()

    def get_psql_binary_dirname(self):
        # type: () -> str
        return self.psql_binary_path.rsplit("/", 1)[0]

    def get_version_and_connection_time(self):
        # type: () -> tuple[str, str]
        usage_start = resource.getrusage(resource.RUSAGE_CHILDREN) # pylint: disable=possibly-used-before-assignment
        out = self.get_server_version()
        usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)

        sys_time = usage_end.ru_stime - usage_start.ru_stime
        usr_time = usage_end.ru_utime - usage_start.ru_utime
        real = sys_time + usr_time

        return out, "%.3f" % real


def pgbouncer_factory(db_user, pg_binary_path, pg_instance):
    # type: (str, str | None, dict[str, str | None]) -> PgbouncerBase
    if IS_LINUX:
        return PgbouncerLinux(db_user, pg_binary_path, pg_instance)
    if IS_WINDOWS:
        return PgbouncerWin(db_user, pg_binary_path, pg_instance)
    raise OSNotImplementedError


def helper_factory():
    # type: () -> Helpers
    if IS_LINUX:
        return LinuxHelpers()
    if IS_WINDOWS:
        return WindowsHelpers()
    raise OSNotImplementedError


class Helpers:
    """
    Base class for x-plattform postgres helper functions

    All abstract methods must have individual implementation depending on the OS type
    which runs postgres.
    All non-abstract methods are meant to work on all OS types which were subclassed.
    """

    __metaclass__ = abc.ABCMeta

    @staticmethod
    @abc.abstractmethod
    def get_default_pgbouncer_user():
        pass

    @staticmethod
    @abc.abstractmethod
    def get_default_path():
        pass

    @staticmethod
    @abc.abstractmethod
    def get_conf_sep():
        pass


class WindowsHelpers(Helpers):
    @staticmethod
    def get_default_pgbouncer_user():
        return "postgres"

    @staticmethod
    def get_default_path():
        return "c:\\ProgramData\\checkmk\\agent\\config"

    @staticmethod
    def get_conf_sep():
        return "|"


class LinuxHelpers(Helpers):
    @staticmethod
    def get_default_pgbouncer_user():
        for user_id in ("pgsql", "postgres"):
            try:
                proc = subprocess.Popen(  # pylint: disable=consider-using-with
                    ["id", user_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                proc.communicate()
                if proc.returncode == 0:
                    return user_id.rstrip()
            except subprocess.CalledProcessError:
                pass
        LOGGER.warning('Could not determine postgres user, using "postgres" as default')
        return "postgres"

    @staticmethod
    def get_default_path():
        return "/etc/check_mk"

    @staticmethod
    def get_conf_sep():
        return ":"


def open_env_file(file_to_open):
    """Wrapper around built-in open to be able to monkeypatch through all python versions"""
    return open(file_to_open, encoding='utf-8').readlines()


def parse_env_file(env_file):
    # type: (str) -> tuple[str, str, str, str | None]
    pg_host = None
    pg_port = None  # mandatory in env_file
    pg_database = "pgbouncer"  # default value
    pg_version = None
    for line in open_env_file(env_file):
        line = line.strip()
        if "PGDATABASE=" in line:
            pg_database = re.sub(re.compile("#.*"), "", line.split("=")[-1]).strip()
        elif "PGHOST=" in line:
            pg_host = re.sub(re.compile("#.*"), "", line.split("=")[-1]).strip()
        elif "PGPORT=" in line:
            pg_port = re.sub(re.compile("#.*"), "", line.split("=")[-1]).strip()
        elif "PGVERSION=" in line:
            pg_version = re.sub(re.compile("#.*"), "", line.split("=")[-1]).strip()
    if pg_port is None:
        raise ValueError("PGPORT is not specified in %s" % env_file)
    return pg_database, pg_host, pg_port, pg_version


def _parse_INSTANCE_value(value, config_separator):
    # type: (str, str) -> tuple[str, str, str, str]
    keys = value.split(config_separator)
    if len(keys) == 3:
        # Old format (deprecated in Werk 16016), but we don't force updates unless there is
        # a substantial benefit.
        keys = keys + [""]
    env_file, pg_user, pg_passfile, instance_name = keys
    env_file = env_file.strip()
    return env_file, pg_user, pg_passfile, instance_name or env_file.split(os.sep)[-1].split(".")[0]


def parse_pgbouncer_cfg(pgbouncer_cfg, config_separator, cfg):
    # type: (list[str], str, dict[str, str | None, str | None, str | None, str | None ]) -> list[dict[str, str | None]]
    """
    Parser for Pgbouncer config. x-Plattform compatible.
    See comment at the beginning of this file for an example.
    """
    instances = []
    for line in pgbouncer_cfg:
        if line.startswith("#") or "=" not in line:
            continue
        line = line.strip()
        key, value = line.split("=")
        value = value.strip('"')
        if key == "DBUSER":
            cfg["dbuser"] = value.rstrip()
        if key == "PG_BINARY_PATH":
            cfg["pg_binary_path"] = value.rstrip()
        if key == "PGDATABASE":
            cfg["pg_database"] = value.rstrip()
        if key == "PGHOST":
            cfg["pg_host"] = value.rstrip()
        if key == "PGPORT":
            cfg["pg_port"] = value.rstrip()
        if key == "PGVERSION":
            cfg["pg_version"] = value.rstrip()
        if key == "PGPASSFILE":
            cfg["pg_passfile"] = value.rstrip()
        if key == "INSTANCE":
            env_file, pg_user, pg_passfile, instance_name = _parse_INSTANCE_value(
                value, config_separator
            )
            pg_database, pg_host, pg_port, pg_version = parse_env_file(env_file)
            instances.append(
                {
                    "name": instance_name,
                    "pg_user": pg_user.strip(),
                    "pg_passfile": pg_passfile.strip(),
                    "pg_database": pg_database,
                    "pg_host": pg_host,
                    "pg_port": pg_port,
                    "pg_version": pg_version,
                }
            )
    return instances


def parse_arguments(argv):
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", action="count", default=0)
    parser.add_option(
        "-t",
        "--test-connection",
        default=False,
        action="store_true",
        help="Test if pgbouncer is ready",
    )
    options, _ = parser.parse_args(argv)
    return options


def main(argv=None):
    # type: (list | None) -> int

    helper = helper_factory()
    if argv is None:
        argv = sys.argv[1:]

    opt = parse_arguments(argv)

    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level={0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG}.get(opt.verbose, logging.DEBUG),
    )

    cfg = {
        "dbuser": helper.get_default_pgbouncer_user(),
        "pg_binary_path": None,
        "pg_database": "pgbouncer",
        "pg_host": None,
        "pg_port": "6432",
        "pg_version": None,
        "pg_passfile": ""
    }
    instances = []  # type: list[dict[str, str | None]]
    try:
        pgbouncer_cfg_path = os.path.join(
            os.getenv("MK_CONFDIR", helper.get_default_path()), "pgbouncer.cfg"
        )
        with open(pgbouncer_cfg_path, encoding='utf-8') as opened_file:
            pgbouncer_cfg = opened_file.readlines()
        instances = parse_pgbouncer_cfg(pgbouncer_cfg, helper.get_conf_sep(), cfg)
    except Exception: # pylint: disable=broad-except
        _, e = sys.exc_info()[:2]  # python2 and python3 compatible exception logging
        LOGGER.debug("try_parse_config: exception: %s", str(e))

    if not instances:
        default_pgbouncer_installation_parameters = {
            # default database name of postgres installation
            "name": "default",
            "pg_user": cfg["dbuser"],
            "pg_database": cfg["pg_database"],
            "pg_host": cfg["pg_host"],
            "pg_port": cfg["pg_port"],
            # Assumption: if no pg_passfile is specified no password will be required.
            # If a password is required but no pg_passfile is specified the process will
            # interactivly prompt for a password.
            "pg_passfile": cfg["pg_passfile"],
        }
        instances.append(default_pgbouncer_installation_parameters)

    for instance in instances:
        pgbouncer = pgbouncer_factory(cfg["dbuser"], cfg["pg_binary_path"], instance)
        if opt.test_connection:
            pgbouncer.is_pg_ready()
            sys.exit(0)
        pgbouncer.execute_all_queries()
    return 0


if __name__ == "__main__":
    main()
