import os
import pickle


class ScoreReader:
    @classmethod
    def write(cls, path, scores=None):
        if scores is None:
            scores = {str(i): 0 for i in range(1, 11)}
        with open(os.path.join(path, 'scores.ptf'), 'wb') as file:
            pickle.dump(scores, file)

    @classmethod
    def load(cls, path):
        file_path = os.path.join(path, 'scores.ptf')
        if not os.path.exists(file_path):
            cls.write(path)
        with open(file_path, 'rb') as file:
            scores = pickle.load(file)
        return scores

    @classmethod
    def update_score(cls, path, level, score):
        scores = cls.load(path)
        scores[level] = max(scores[level], score)
        cls.write(path, scores)
