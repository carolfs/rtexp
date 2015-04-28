#Copyright 2014, 2015 Carolina Feher da Silva
#
#This file is part of rtexp.
#
#rtexp is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#rtexp is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with rtexp.  If not, see <http://www.gnu.org/licenses/>.

import random
import sys
import math

# Maximum time the target can appear
tmax = None

# Side the target will appear (L = left, R = right)
l = 'L' # The target will be *always* on the left

# Returns a value proportional to the likelihood of a random variable
# with normal distribution ~ N(mi, sigma^2)
def likelihood(x, mi, sigma):
    return math.exp(-(x - mi) ** 2 / (2 * sigma ** 2))

# Cumulative probabilility that the target has appeared on the left
def acProbAe(t, r):
    return r * t / tmax

# Cumulative probabilility that the target has appeared on the right
def acProbAd(t, r):
    return (1 - r) * t / tmax

# Cumulative probabilility that the target has not appeared
def acProbnA(t):
    return (tmax - t) / tmax

# Probabilility that the target has appeared on instant t
# r: probability that the stimulus will appear on the left
# as given by the cue
def probA(t, l, r):
    if l == 'L':
        return r / tmax
    else:
        assert l == 'R'
        return (1 - r) / tmax

# Cumulative probabilility that the target has appeared on side l
def acProbA(t, l, r):
    if l == 'L':
        return r * t / tmax
    else:
        assert l == 'R'
        return (1 - r) * t / tmax

# Stimulus likelihood, given that the target has already appeared on the left
def lSAe(S, s, sigma):
  Se, Sd = S
  return likelihood(Se, s, sigma) * likelihood(Sd, 0, sigma)

# Stimulus likelihood, given that the target has already appeared on the right
def lSAd(S, s, sigma):
    Se, Sd = S
    return likelihood(Se, 0, sigma) * likelihood(Sd, s, sigma)

# Stimulus likelihood, given that the target has not appeared yet
def lSnA(S, s, sigma):
    Se, Sd = S
    return likelihood(Se, 0, sigma) * likelihood(Sd, 0, sigma)

# Returns a stimulus for time t
# t: the side the target will appear
# ta: the time the target will appear
# s: signal intensity
# sigma: noise intensity
def S(t, l, ta, s, sigma):
    if t < ta:
        return (random.gauss(0, sigma), random.gauss(0, sigma))
    else:
        if l == 'L':
            return (random.gauss(s, sigma), random.gauss(0, sigma))
        else:
            assert l == 'R'
            return (random.gauss(0, sigma), random.gauss(s, sigma))

# Likelihood of a stimulus sequence, given that the target
# has appeared on a side at time ta
def lSeq(Seq, ta, side):
    l = 1
    for i, S in enumerate(Seq):
        t = i + 1
        if t < ta:
            l *= lSnA(S, s, sigma)
        else:
            if side == 'L':
                l *= lSAe(S, s, sigma)
            else:
                assert side == 'R'
                l *= lSAd(S, s, sigma)
    return l

# Likelihood of a stimulus sequence, given that the target
# has appeared on a side
def lSeqA(Seq, side, r):
    l = 0
    for t in range(1, len(Seq) + 1):
        l += lSeq(Seq, t, side) * probA(t, side, r)
    return l

# Likelihood of a stimulus sequence, given that the target
# has not appeared yet
def lSeqCondnA(Seq):
    l = 1
    for S in Seq:
        l *= lSnA(S, s, sigma)
    return l

# Slowest trial function
# It calculates the probabilities as described in the article
def trial_noncumulative(Seq, r, ta, s, sigma):
    for t in range(1, len(Seq) + 1):
        thisSeq = Seq[:t]
        assert len(thisSeq) == t
        numAe = lSeqA(thisSeq, 'L', r)
        numAd = lSeqA(thisSeq, 'R', r)
        numnA = lSeqCondnA(thisSeq) * acProbnA(t)
        den = numAe + numAd + numnA
        yield numAe / den, numAd / den
  
# Faster trial function
def trial2(Seq, r, ta, s, sigma):
    numAe = 0
    numAd = 0
    numnA = 1
    
    for t, S in zip(range(1, tmax + 1), Seq):
        # Only works for 1 <= t <= tmax!
        numAe = numAe * lSAe(S, s, sigma) + numnA / acProbnA(t - 1) * lSAe(S, s, sigma) * (r / tmax)
        numAd = numAd * lSAd(S, s, sigma) + numnA / acProbnA(t - 1) * lSAd(S, s, sigma) * ((1 - r) / tmax)
        numnA = lSnA(S, s, sigma) * numnA * (tmax - t) / (tmax - t + 1)
        den = numAe + numAd + numnA
        yield numAe / den, numAd / den

def prob_target(cue, t):
    if t < tmax:
        return cue / (tmax - t + 1)
    else:
        return cue

def prob_not_target(t):
    if t < tmax:
        return (tmax - t) / (tmax - t + 1)
    else:
        return 0

# Faster trial function
def trial(Seq, r, ta, s, sigma):
    probAe = 0 # Probability that the target has appeared on the left
    probAd = 0 # Probability that the target has appeared on the right
    probnA = 1 # Probability that the target has not appeared yet
  
    for t, S in zip(range(1, len(Seq) + 1), Seq):
        probAe = lSAe(S, s, sigma) * (probAe + probnA * prob_target(r, t))
        probAd = lSAd(S, s, sigma) * (probAd + probnA * prob_target(1 - r, t))
        probnA = lSnA(S, s, sigma) * probnA * prob_not_target(t)
        den = probAe + probAd + probnA
        probAe /= den
        probAd /= den
        probnA /= den
        yield probAe, probAd

def mean_stder(l):
    m = sum(l) / len(l)
    v = sum([(i - m) ** 2 for i in l]) / (len(l) - 1)
    stdev = math.sqrt(v)
    return str(m) + '\t' + str(stdev / math.sqrt(len(l)))

if __name__ == '__main__':
    # Parameters
    try:
        s = float(sys.argv[1]) # Intensity of target stimulus
        assert s > 0
        sigma = float(sys.argv[2]) # Intensity of noise
        assert sigma > 0
        tmax = int(sys.argv[3]) # Maximum time the target can appear
        assert tmax > 0
        # Probability that the target will appear on the left (given by the cue)
        r = float(sys.argv[4])
        assert 0.5 < r and r <= 1
    except:
        print("This script expects four parameters:")
        print("  1. s: stimulus intensity, s > 0")
        print("  2. sigma: noise intensity, sigma > 0")
        print("  3. tmax: maximum time the target can appear")
        print("  4. r: probability that the target will appear "\
              "on the left, given by a valid cue (0.5 < r <= 1)")
        sys.exit(0)
  
    # Runs a trial of an RT experiment
    
    # When will the target appear?
    ta = random.randint(1, tmax)
    # Sequence of stimuli
    Seq = [S(i + 1, l, ta, s, sigma) for i in range(tmax * 10)]
    # Run trial
    for t, (ve, vd), (ne, nd), (ive, ivd) in zip(range(1, tmax * 10 + 1), trial(Seq, r, ta, s, sigma), trial(Seq, 0.5, ta, s, sigma), trial(Seq, 1 - r, ta, s, sigma)):
        print(t, ve, vd, ne, nd, ive, ivd, sep="\t")
        assert (ve >= ne and ne >= ive and vd <= nd and vd <= ivd)
        assert(ve > ive or ive == 1)
        assert(vd < ivd or vd == 1)
    assert (ve + vd >= (1 - 1e-10) and ne + nd >= (1 - 1e-10) and ive + ivd >= (1 - 1e-10))
  