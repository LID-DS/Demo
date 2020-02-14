class Statistic:

    syscall_sum = None
    data_handling = None

    def __init__(self, data_handling):
        self.data_handling = data_handling
    
    def calc_new_statistic(self):
        self.calc_sum()

    def calc_sum(self):
        #tmp_count = rethink_db.table("statistics").filter
        #rethink_db.table("statistics").update({"sum": global_test_counter})
        sum_syscalls = self.data_handling.get_sum() 
        print("calc")
        print(sum_syscalls)
        self.data_handling.update_statistics(sum_syscalls + 1)
        self.sum = sum_syscalls + 1

        return None
