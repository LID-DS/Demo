from rethinkdb import RethinkDB

class DataHandling:

    rethink_db = None
    
    def __init__(self):
        self.rethink_db = self.create_db()
        self.insert()
        
    def create_db(self):
        r = RethinkDB()
        r.connect("localhost", 28015).repl()
        r.table("statistics").delete().run()
        
        #r.db('test').table_create("statistics").run()
        return r

    def insert(self): 
        self.rethink_db.table("statistics").insert({
             "sum": 0
            }
            ).run()

    def get_db(self):
        cursor = self.rethink_db.table("statistics").run()
        testlist = []
        for document in cursor:
            testlist.append(document)
        print(testlist)
        return self.rethink_db.table("statistics")
