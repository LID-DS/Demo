from demo_model_stide import DemoModelStide
class IDSWrapper:

    def __init__(self, stide: bool, mlp:bool):
        """
        Handling of chosen IDS 
        multiple IDSs possible
        Instances of different IDS are passed as list
        """

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
                'score' : 0,
                'score_list' : [], 
                'state' : self.stide._model_state.value,
                'training_size' : self.stide._training_size,
                'current_ngrams' : 0 
                }

    def init_mlp(self):
        """
        Initialisation of mlp algorithm
        """
        self.mlp = None
        self.active_ids["mlp"] = self.mlp

    def set_active_ids(self, active_ids):
        """
        receive active ids information of frontend
        """
        print(active_ids["stide"])
        print(active_ids["mlp"])
        # do nothing if active_ids["stide"] is true and stide was active
        if active_ids["stide"] and self.active_ids["stide"]:
            pass
        # activate stide if param is true and stide was not active
        elif active_ids["stide"] and not self.active_ids["stide"]:
            self.active_ids["stide"] = self.init_stide()
        # if param is false stop sending syscalls to stide
        elif not active_ids["stide"]:
            self.active_ids["stide"] = None
            print("stide down")
        # do nothing if active_ids["mlp"] is true and mlp was active
        if active_ids["mlp"] and self.active_ids["mlp"]:
            pass
        # activate mlp if param is true and mlp was not active
        elif active_ids["mlp"] and not self.active_ids["mlp"]:
            self.active_ids["stide"] = self.init_stide()
        # if param is false stop sending syscalls to mlp
        elif not active_ids["mlp"]:
            self.active_ids["mlp"] = None


    def send_to_ids(self, syscall):
        """
        Return collected information of all active ids
        """
        if not self.active_ids["stide"] is None:
            ids_score = self.stide.consume_system_call(syscall)
            if not ids_score is None: 
                self.global_ids_info["stide"]["score_list"].append(ids_score)
            ids_info = { 
                    'score' : ids_score,
                    'score_list' : self.global_ids_info["stide"]["score_list"],
                    'state' : self.stide._model_state.value,
                    'training_size' : self.stide._training_size,
                    'current_ngrams' : self.stide._normal_ngrams["training_size"],
                    }
            self.global_ids_info["stide"] = ids_info
        if "mlp" in self.active_ids.keys():
            self.global_ids_info["mlp"] = None
        return self.global_ids_info

    def get_ids_score(self):
        """
        return score of all active ids
        """
        # if list is not empty return highest score
        score_list = self.global_ids_info["stide"]['score_list']
        if score_list:
            # sort list and return highest score
            sorted_ids_scores = sorted(
                    score_list,
                    reverse=True)
            self.global_ids_info["stide"]['score_list'] = list()
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

