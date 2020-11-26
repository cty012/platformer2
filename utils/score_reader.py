import os
import pickle


class ScoreReader:
    @classmethod
    def write(cls, path, scores=None):
        if scores is None:
            scores = {str(i): [-1, None] for i in range(1, 11)}
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
    def update_score(cls, path, level, score, str_time):
        scores = cls.load(path)
        list_time = [int(i) for i in str_time.split(":")]
        time = list_time[0] * 6000 + list_time[1] * 100 + list_time[2]
        if time >= 360000:
            time = None
        if score == scores[level][0]:
            if time is not None:
                scores[level][1] = time if scores[level][1] is None else min(scores[level][1], time)
        if score > scores[level][0]:
            scores[level][0] = score
            scores[level][1] = time
        cls.write(path, scores)
