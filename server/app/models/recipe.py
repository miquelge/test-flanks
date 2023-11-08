
class Recipe(object):
    def __init__(self, title, introduction, url, diners, duration, difficulty, ingredients, steps):
        self.title = title
        self.introduction = introduction
        self.url = url
        self.diners = diners
        self.duration = duration
        self.difficulty = difficulty
        self.ingredients = ingredients
        self.steps = steps

    def print(self):
        print(self.title)
        print(self.introduction)
        print(self.url)
        print(self.diners)
        print(self.duration)
        print(self.difficulty)
        print('Ingredients:')
        for i in self.ingredients:
            print('    ' + i)
        print('Steps: ')
        for step in self.steps:
            print(step)

    def json(self):
        return {
            'title': self.title,
            'introduction': self.introduction,
            'url': self.url,
            'diners': self.diners,
            'duration': self.duration,
            'difficulty': self.difficulty,
            'ingredients': self.ingredients,
            'steps': self.steps
        }
