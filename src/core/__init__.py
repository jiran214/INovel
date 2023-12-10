class A:
    def __iter__(self):
        return self

    def next(self):
        for _ in range(5):
            print(1)
            a = (yield)
            print('2', a)


iter_obj = A().next()
print(iter_obj.send(None))