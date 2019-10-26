


def pickle_decorator(func, num_args, to_pickle=True):
    import pickle

    def funcall(*args, **kwargs):
        if to_pickle:
            for arg, index in enumerate(args):
                filename = f'arg{index}.pickle'
                pickle.dump(arg, open(filename, 'wb'))

                for key, val in kwargs.items():
                    filename = f'arg_{key}.pickle'
                    pickle.dump(arg, open(filename, 'wb'))
            else:
                filenames = [f'arg{index}.pickle' for index in range(num_args)]
                args = [
                    pickle.load(open(filename, 'wb')) for filename in filenames
                ]

                for key, val in kwargs.items():
                    filename = f'arg_{key}.pickle'
                    pickle.dump(arg, open(filename, 'wb'))

    return funcall(*args, **kwargs)

    # Dump contents

    # import pickle
    # pickle.dump(background, open('background.pickle','wb'))
    # pickle.dump(scale, open('scale.pickle','wb'))
    # pickle.dump(offset, open('offset.pickle','wb'))
    # print('written pickle!')

    # import pickle
    # background = pickle.load(open('background.pickle', 'rb'))
    # scale = pickle.load(open('scale.pickle', 'rb'))
    # offset = pickle.load(open('offset.pickle', 'rb'))
