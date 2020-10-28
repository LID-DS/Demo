from demo_model_stide import DemoModelStide
#from mlp import MLP
from syscalls_to_vec_mlp import SyscallsToVec


class IDSWrapper:

    def __init__(self, stide: bool, mlp:bool):
        """
        Handling of chosen IDS 
        multiple IDSs possible
        Instances of different IDS are passed as list
        """
        self.key = ""
        self.active_ids = {
                "stide": None,
                "mlp" : None} 
        self.global_ids_info = {} 
        if mlp: self.init_mlp()
        if stide: self.init_stide()

    def load_active_models(self):
        if self.active_ids["stide"]:
            trained_model = self.stide._load_model()
            self.init_stide(trained_model=trained_model)
        if self.active_ids["mlp"]:
            #trained_model = self.mlp._load_model()
            #self.init_mlp(trained_model=trained_model)
            print("load pretrained mlp model")

    def init_stide(self, training_size=None, trained_model=None):
        """
        Initialisation of stide algorithm
        """
        self.key = "stide"
        # use default values
        if training_size is None and trained_model is None:
            self.stide = DemoModelStide(ngram_length=7, window_length=3, training_size=10000000) 
        # use predefined training size
        elif not training_size is None:
            self.stide = DemoModelStide(ngram_length=7, window_length=3, training_size=training_size) 
        # use already trained model
        elif not trained_model is None:
            self.stide = DemoModelStide(trained_model=trained_model)
        self.active_ids["stide"] = self.stide
        self.global_ids_info["stide"] = {
            'score': 0,
            'state': self.stide._model_state.value,
            'training_size': self.stide._training_size,
            'current_ngrams': 0 
        }
        self.score_list = []
        print("Stide initialized")

    def init_mlp(self):
        """
        Initialisation of mlp algorithm
        """
        self.key = "mlp"
        syscall_map = SyscallsToVec()
        self.mlp = "smth"#MLP(syscall_map)
        self.active_ids["mlp"] = self.mlp
        self.global_ids_info["mlp"] = {
                'score': 0,
                'state': 0
                }
        self.score_list = []
        print("MLP initialized")

    def set_active_ids(self, active_ids):
        """
        receive active ids information of frontend
        """
        # do nothing if active_ids["stide"] is true and stide was active
        if active_ids["stide"] and self.active_ids["stide"]:
            pass
        # activate stide if param is true and stide was not active
        elif active_ids["stide"] and not self.active_ids["stide"]:
            self.init_stide()
        # if param is false stop sending syscalls to stide
        elif not active_ids["stide"]:
            self.active_ids["stide"] = None
            print("stide down")
        # do nothing if active_ids["mlp"] is true and mlp was active
        if active_ids["mlp"] and self.active_ids["mlp"]:
            pass
        # activate mlp if param is true and mlp was not active
        elif active_ids["mlp"] and not self.active_ids["mlp"]:
            self.init_mlp()
        # if param is false stop sending syscalls to mlp
        elif not active_ids["mlp"]:
            self.active_ids["mlp"] = None
        print(self.active_ids)


    def send_to_ids(self, syscall):
        """
        Return collected information of all active ids
        """
        if self.active_ids["stide"] is not None:
            ids_score = self.stide.consume_system_call(syscall)
            if ids_score is not None: 
                self.score_list.append(ids_score)
            ids_info = { 
                    #'score' : self.get_ids_score_last_second(),
                    'state' : self.stide._model_state.value,
                    'training_size' : self.stide._training_size,
                    'current_ngrams' : self.stide._normal_ngrams["training_size"],
                    }
            self.global_ids_info["stide"] = ids_info
            #print(ids_info['score'])
        if self.active_ids["mlp"] is not None:
            ids_score = 0.5
            if ids_score is not None:
                self.score_list.append(ids_score)
            ids_info = {
                    #'score' : self.get_ids_score_last_second(),
                    'state' : 1,
                    }
            self.global_ids_info["mlp"] = ids_info
        return self.global_ids_info

    def get_ids_score_last_second(self):
        """
        return score of all active ids
        """
        # if list is not empty return highest score
        if self.score_list:
            # sort list and return highest score
            sorted_ids_scores = sorted(
                    self.score_list,
                    reverse=True)
            self.score_list = list()
            highest_score = sorted_ids_scores[0]
            return highest_score
        return 0

    def save_active_model(self):
        """
        save all trained models
        """
        if self.active_ids["stide"]:
            self.stide._save_model()
        if self.active_ids["mlp"]:
            print("save mlp model")

