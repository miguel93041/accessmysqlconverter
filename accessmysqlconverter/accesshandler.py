"""
Class that gets column strucutre, vartypes, etc... intermediary between access file and sql file
"""


from os import path
from tkinter import messagebox

from accessmysqlconverter.otherfileformatter import Otherfileformatter
from accessmysqlconverter.postgresfileformatter import Postgresfileformatter


class Accesshandler:
    """Class used to get the tables, columns of an access file"""
    def __init__(self, cur):
        self._cur = cur

    def make_file(self, output_dir, database_name, db_type):
        """Makes sql file"""
        table_names = self._sort_tables(self._get_table_names(), db_type)
        suffix = ".sql"
        file = open("{}".format(path.join(output_dir, database_name + suffix)), "w+", encoding='utf-8')

        from accessmysqlconverter.application import Application
        fileformatter = Postgresfileformatter(file, self._get_tables(db_type)) if db_type == Application.DB_TYPE_POSTGRESQL() else Otherfileformatter(file, self._get_tables(db_type))
        fileformatter.write_header(database_name)
        for name in table_names:
            fileformatter.write_table(name, self._get_columns(name, db_type))

        MsgBox = messagebox.askquestion('Import data', 'Do you want to import the data?', icon='warning')
        if MsgBox == "yes":
            for name in table_names:
                fileformatter.write_table_data(name, self._get_table_columns(name), self._get_table_data(name))

        file.close()

    def _get_table_names(self):
        """Retrieves a list with the names of the tables"""
        tables = list()
        for table in self._cur.tables(tableType="TABLE"):
            name = table[2]
            if name[0] != "~":        # Sometimes you get strange tables like ~TR324XZ0 so we need to filter them
                tables.append(name)
        return tables

    def _sort_tables(self, table_names, db_type):
        default_table_names = list()
        table_names_with_index = list()
        table_names_with_many2many = list()

        for table_name in table_names:
            primary_key_count = 0
            columns = self._get_columns(table_name, db_type)
            for column in columns:
                column_name = column[0]
                is_primary_key = column[3]
                if is_primary_key:
                    primary_key_count += 1
                    if primary_key_count > 1:
                        table_names_with_many2many.append(table_name)
                        break
                elif column_name.lower().find("id") != -1:
                    table_names_with_index.append(table_name)
                    break
                elif column == columns[-1]:
                    default_table_names.append(table_name)
        return default_table_names + table_names_with_index + table_names_with_many2many

    def _get_tables(self, db_type):
        """Gets a list of tables and It's columns for Postgres"""
        tables = list()
        table_names = self._get_table_names()
        for table_name in table_names:
            column_names = list()
            for column in self._get_columns(table_name, db_type):
                is_primary_key = column[3]
                if is_primary_key:
                    column_name = column[0]
                    column_names.append(column_name)
            tables.append((table_name, column_names))
        return tables

    def _get_columns(self, table_name, db_type):
        """Gets from a table it's columns with it's var names, types..."""
        formatted_columns = list()
        table_columns = self._get_table_columns(table_name)
        table_columns_statistics = self._get_table_columns_statistics(table_name)

        for column in table_columns:
            column_name = column[3]
            column_var_type = column[5]
            column_var_size = column[6]

            # Transform ACCESS VARTYPE to SQL VARTYPE
            from accessmysqlconverter.application import Application
            if db_type == Application.DB_TYPE_POSTGRESQL():
                column_var_sql_type = self._get_postgres_data_type(column_var_type)
            elif db_type == Application.DB_TYPE_MARIADB():
                column_var_sql_type = self._get_mariadb_data_type(column_var_type)
            else:
                column_var_sql_type = self._get_mysql_data_type(column_var_type)

            column_is_primary_key = self._is_primary_key(table_columns_statistics, column_name)
            column_is_auto_increment = column_var_type == "COUNTER"

            formatted_columns.append((column_name, column_var_sql_type, column_var_size, column_is_primary_key, column_is_auto_increment))
        return formatted_columns

    def _get_table_columns(self, table_name):
        """Retrieves a list with the columns of the given table"""
        columns = list()
        cur_columns = self._cur.columns(table=table_name)
        for column in cur_columns:
            columns.append(column)

        return columns

    def _get_table_columns_statistics(self, table_name):
        """Retrieves a list with the columns statistics of the given table (useful for keys)"""
        columns_statistics = list()
        for column in self._cur.statistics(table_name):
            columns_statistics.append(column)
        return columns_statistics

    def _get_postgres_data_type(self, access_type):
        """Access vartypes to PostgreSQL vartypes"""
        switcher = {
            "LONGBINARY": "bytea",
            "BIT": "bit",
            "COUNTER": "int",
            "CURRENCY": "money",
            "GUID": "int",
            "DOUBLE": "double",
            "INTEGER": "int",
            "BYTE": "int",
            "SMALLINT": "smallint",
            "DECIMAL": "float",
            "REAL": "real",
            "DATETIME": "timestamp",
            "VARCHAR": "varchar",
            "LONGCHAR": "text"
        }
        return switcher.get(access_type, "varchar")

    def _get_mariadb_data_type(self, access_type):
        """Access vartypes to MariaDB vartypes"""
        switcher = {
            "LONGBINARY": "varbinary",
            "BIT": "bit",
            "COUNTER": "int",
            "CURRENCY": "float",
            "GUID": "int",
            "DOUBLE": "double",
            "INTEGER": "int",
            "BYTE": "int",
            "SMALLINT": "smallint",
            "DECIMAL": "float",
            "REAL": "double",
            "DATETIME": "datetime",
            "VARCHAR": "varchar",
            "LONGCHAR": "longtext"
        }
        return switcher.get(access_type, "varchar")

    def _get_mysql_data_type(self, access_type):
        """Access vartypes to MySQL vartypes"""
        switcher = {
            "LONGBINARY": "varbinary",
            "BIT": "bit",
            "COUNTER": "int",
            "CURRENCY": "money",
            "GUID": "int",
            "DOUBLE": "double",
            "INTEGER": "int",
            "BYTE": "int",
            "SMALLINT": "smallint",
            "DECIMAL": "float",
            "REAL": "real",
            "DATETIME": "datetime",
            "VARCHAR": "varchar",
            "LONGCHAR": "longtext"
        }
        return switcher.get(access_type, "varchar")

    def _is_primary_key(self, table_columns, pColumn_name):
        """Check if column is primary key"""
        for column in table_columns:
            column_name = column[8]
            column_primary_Key = column[5]
            if column_name == pColumn_name and column_primary_Key == "PrimaryKey":
                return True
        return False

    def _get_table_data(self, table_name):
        """Simple query to fetch all data inside a table"""
        self._cur.execute("SELECT * FROM `{}`".format(table_name))
        return self._cur.fetchall()
