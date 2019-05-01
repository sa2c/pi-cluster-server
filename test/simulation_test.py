from kinectlib.kinectlib import depth_to_depthimage


def get_test_simulations():
    print('loading simulations...')
    data = np.load('sim.npy')
    depths = np.load('sim.npy')
    depthimages = [depth_to_depthimage(depth) for depth in depths]

    simulations = {
        '23454325': {
            'name': 'Bob Jones',
            'score': 10.5,
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '3445345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        },
        '234523452': {
            'name': 'Bob Jones',
            'score': 10.5,
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '23452345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        }
    }

    print('simulations loaded')
    return simulations
