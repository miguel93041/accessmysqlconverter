"""
This class handles the writing of the SQL File
"""
from accessmysqlconverter.fileformatterinterface import Fileformatterinterface


class Otherfileformatter(Fileformatterinterface):
    """Creates a MySQL/MariaDB, etc SQL File"""
    def __init__(self, file, tables):
        self.file = file
        self.tables = tables

    def write_header(self, database_name):
        """Overrides Fileformatterinterface.write_header()"""
        print("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';", file=self.file)
        print("SET time_zone = '+00:00';", file=self.file)
        print("", file=self.file)
        print("--", file=self.file)
        print("-- Database: `{}`".format(database_name), file=self.file)
        print("--", file=self.file)
        print("CREATE DATABASE IF NOT EXISTS `{}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;".format(database_name), file=self.file)
        print("USE `{}`;".format(database_name), file=self.file)
        print("", file=self.file)

    def write_table(self, table_name, formatted_columns):
        """Overrides Fileformatterinterface.write_table()"""
        vars_with_no_size = ["money", "double", "datetime", "longtext", "real"]
        primary_keys = self._get_primary_keys(formatted_columns)
        index_keys = self._get_index_keys(formatted_columns)

        print("--", file=self.file)
        print("-- Table structure for table `{}`".format(table_name), file=self.file)
        print("--", file=self.file)
        print("CREATE TABLE `{}` (".format(table_name), file=self.file)

        for column in formatted_columns:
            column_name, column_var_type, column_var_size, _, column_is_auto_increment = column

            line = "`{}` {}".format(column_name, column_var_type)
            if column_var_type not in vars_with_no_size:
                line += "({})".format(column_var_size)
            line += " NOT NULL"
            if column_is_auto_increment:
                line += " AUTO_INCREMENT"

            if primary_keys.__len__() > 0 or index_keys.__len__() > 0 or column != formatted_columns[-1]:
                line += ","
            print(line, file=self.file)

        if primary_keys.__len__() > 0:
            primary_line = "PRIMARY KEY ("
            for primary_key_name in primary_keys:
                primary_line += "`{}`".format(primary_key_name)
                if primary_key_name != primary_keys[-1]:
                    primary_line += ", "
            primary_line += ")"
            if index_keys.__len__() > 0 or primary_keys.__len__() > 1:
                primary_line += ","
            print(primary_line, file=self.file)
            if primary_keys.__len__() > 1:
                for primary_key_name in primary_keys:
                    referenced_table = self._get_origin_table(table_name, primary_key_name)
                    if referenced_table != "":
                        print("FOREIGN KEY (`{}`)".format(primary_key_name), file=self.file)
                        references_format = "  REFERENCES `{}` (`{}`)".format(referenced_table, primary_key_name)
                        if primary_key_name != primary_keys[-1] or index_keys.__len__() > 0:
                            references_format += ","
                        print(references_format, file=self.file)

        if index_keys.__len__() > 0:
            for index_key_name in index_keys:
                referenced_table = self._get_origin_table(table_name, index_key_name)
                index_line = "INDEX `{0}` (`{0}`)".format(index_key_name)
                if index_key_name != index_keys[-1] or referenced_table != "":
                    index_line += ", "
                print(index_line, file=self.file)
                if referenced_table != "":
                    print("FOREIGN KEY (`{}`)".format(index_key_name), file=self.file)
                    references_format = "  REFERENCES `{}` (`{}`)".format(referenced_table, index_key_name)
                    if index_key_name != index_keys[-1]:
                        references_format += ","
                    print(references_format, file=self.file)
        print(") ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=1;", file=self.file)

    def _get_primary_keys(self, formatted_columns):
        """Overrides Fileformatterinterface._get_primary_keys()"""
        primary_keys = list()
        for column in formatted_columns:
            column_is_primary_key = column[3]
            if column_is_primary_key:
                column_name = column[0]
                primary_keys.append(column_name)
        return primary_keys

    def _get_index_keys(self, formatted_columns):
        """Overrides Fileformatterinterface._get_index_keys()"""
        index_keys = list()
        for column in formatted_columns:
            column_name = column[0]
            column_is_primary_key = column[3]
            if not column_is_primary_key and column_name.lower().find("id") != -1:
                index_keys.append(column_name)
        return index_keys

    def _get_origin_table(self, referenced_table_name, column_name):
        """Overrides Fileformatterinterface._get_origin_table()"""
        for table in self.tables:
            table_name, primary_keys = table
            for primary_key in primary_keys:
                if primary_key == column_name and table_name != referenced_table_name:
                    return table_name
        return ""

    def write_table_data(self, table_name, columns, data):
        """Overrides Fileformatterinterface.write_table_data()"""
        if len(data) != 0:
            print("--", file=self.file)
            print("-- Data for table `{}`".format(table_name), file=self.file)
            print("--", file=self.file)
            self._write_table_insert_header(columns, table_name)
            self._write_table_insert_values(columns, data)

    def _write_table_insert_header(self, columns, table_name):
        """Overrides Fileformatterinterface._write_table_insert_header()"""
        insert_header = "INSERT INTO `{}` (".format(table_name)
        for column in columns:
            column_name = column[3]
            insert_header += "`{}`".format(column_name)
            if column != columns[-1]:
                insert_header += ", "
        insert_header += ") VALUES"
        print(insert_header, file=self.file)

    def _write_table_insert_values(self, columns, data):
        """Overrides Fileformatterinterface._write_table_insert_values()"""
        for row in data:
            insert_value = self._get_table_insert_value(columns, row)
            if row != data[-1]:
                insert_value += ","
            else:
                insert_value += ";"
            print(insert_value, file=self.file)

    def _get_table_insert_value(self, columns, row):
        """Overrides Fileformatterinterface._get_table_insert_value()"""
        insert_value = "("
        value_index = 0
        for value in row:
            var_type = columns[value_index][5]
            if var_type == "DATETIME":  # Transform DATETIME var into STRING
                value = "{}".format(value)
            if isinstance(value, str):
                # Check if char \ is in string
                index = value.find("\\")
                for _ in range(value.count("\\")):
                    value = value[:index] + '\\' + value[index:]
                    index = value.find("\\", index + 2)
                # Check if char ' is in string
                index = value.find("\'")
                for _ in range(value.count("\'")):
                    value = value[:index] + '\\' + value[index:]
                    index = value.find("\'", index + 2)
                index = value.find("\"")
                # Check if char " is in string
                for _ in range(value.count("\"")):
                    value = value[:index] + '\\' + value[index:]
                    index = value.find("\"", index + 2)
                insert_value += "'{}'".format(value)
            elif value is not None:
                insert_value += "{}".format(value)
            else:
                insert_value += "'{}'".format("")

            if value_index != (columns.__len__() - 1):
                insert_value += ", "
            value_index += 1
        insert_value += ")"
        return insert_value
