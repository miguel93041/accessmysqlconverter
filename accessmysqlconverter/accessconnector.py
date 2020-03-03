"""
This module is used to connect/link to the access file
"""


from os import path
from pyodbc import connect, drivers as pyodrivers, SQL_WVARCHAR, Error


class AccessConnectionError(Exception):
    pass


class ODBCDriverNotFoundError(Exception):
    pass


class Accessconnector:

    @staticmethod
    def driver(file_path):
        """Gets ODBC driver, if not found throw exception"""
        drivers = [x for x in pyodrivers() if x.startswith('Microsoft Access Driver')]
        extension = path.splitext(file_path)[1]
        error_text = """
                     To use this tool you need to have installed 'Microsoft Access Database Engine 2010 Redistributable'.
                     It can be found in the following link: https://www.microsoft.com/en-US/download/details.aspx?id=13255
            
                     'Microsoft Access Database Engine 2010 Redistributable' is a set of components that can be used to facilitate transfer
                     of data between 2010 Microsoft Office System files and non-Microsoft Office applications.
                     """

        if drivers.__len__() == 0:
            raise ODBCDriverNotFoundError(error_text)
        elif extension == ".accdb":
            accdb_drivers = [x for x in drivers if x.endswith('*.accdb)')]
            if accdb_drivers.__len__() == 0:
                raise ODBCDriverNotFoundError(error_text)
            else:
                return accdb_drivers[0]
        else:
            return drivers[0]

    def con(self, driver, file_path, password):
        """Connect to access file, if any error is found during connection, throw exception"""
        try:
            con = connect('DRIVER={};DBQ={};PWD={}'.format(driver, file_path, password))
            con.add_output_converter(SQL_WVARCHAR, self._decode_sketchy_utf16)
            return con
        except Error as ex:
            raise AccessConnectionError(ex.args[1])

    @staticmethod
    def _decode_sketchy_utf16(raw_bytes):
        """Method for ignoring utf-16le chars"""
        s = raw_bytes.decode("utf-16le", "ignore")
        try:
            n = s.index('\u0000')
            s = s[:n]  # respect null terminator
        except ValueError:
            pass
        return s
