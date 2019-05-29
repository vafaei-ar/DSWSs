def ruler1(truth):
    obs = truth+np.random.normal(0,0.03)
    return obs

def ruler2(truth):
    obs = truth+np.random.normal(0.05,0.03)
    return obs

def ruler3(truth):
    obs = truth+np.random.normal(0,0.01)
    return obs

def ruler4(truth):
    obs = truth+np.random.normal(0.01,0.01)
    return obs
