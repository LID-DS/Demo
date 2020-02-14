from rethinkdb import RethinkDB
import json

class DataHandling:

    rethink_db = None
    conn = None
    
    def __init__(self):
        self.rethink_db = self.create_db()
        self.insert()
        
    def create_db(self):
        self.rethink_db = RethinkDB()
        self.conn = self.rethink_db.connect("localhost", 28015).repl()
        self.rethink_db.table("statistics").delete().run(self.conn)
        
        #r.db('test').table_create("statistics").run()
        return self.rethink_db

    def insert(self): 
        self.rethink_db.table("statistics").insert({
            'sum': 0
        }
        ).run()

    def get_table(self):
        return self.rethink_db.table("statistics")

    def get_sum(self):
        cursor = self.rethink_db.table("statistics").run(self.conn)
        testlist = []
        for document in cursor:
            testlist.append(document)
        sum_syscalls = testlist[0]["sum"]
        return sum_syscalls

    def update_statistics(self,sum_syscalls):
        self.rethink_db.table("statistics").filter({"sum"}).update({
           "sum": sum_syscalls 
        }).run(self.conn)

    def create_json(stats):
        return json.loads('{"sum":' + str(stats) + '}')
