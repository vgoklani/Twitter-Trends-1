"""CS 61A Project 2
Name: Arash Sean Mozarmi
Login: cs61a-ae
TA: Stephen Martinis
Section: 101
"""

"""Visualizing Twitter Sentiment Across America"""

import string
from data import word_sentiments, load_tweets, get_data
from geo import us_states, geo_distance, make_position, longitude, latitude
from maps import draw_state, draw_name, draw_dot, wait
from ucb import main, trace, interact, log_current_line
from idict import *
from doctest import testmod


# Phase 1: The feelings in tweets

def make_tweet(text, time, lat, lon):
    """Return a tweet, represented as an immutable dictionary.    

    text -- A string; the text of the tweet, all in lowercase
    time -- A datetime object; the time that the tweet was posted
    lat -- A number; the latitude of the tweet's location
    lon -- A number; the longitude of the tweet's location
    """
    return make_idict(('text', text), ('time', time), ('latitude', lat), ('longitude', lon))

def tweet_words(tweet):
    """Return a tuple of words in the tweet.

    
    Arguments:
    tweet -- a tweet abstract data type.
    
    Return 1 value:
     - The list of words in the tweet.
    """
    "*** YOUR CODE HERE ***"
    return extract_words(idict_select(tweet, 'text'))


def tweet_location(tweet):
    """Return a position (see geo.py) that represents the tweet's location."""
    "*** YOUR CODE HERE ***"
    return make_position(idict_select(tweet, 'latitude'), idict_select(tweet, 'longitude'))

def tweet_string(tweet):
    """Return a string representing the tweet."""
    return '"{0}" @ {1}'.format(idict_select(tweet, 'text'), tweet_location(tweet))

def extract_words(text):
    """Return a tuple of the words in a tweet, not including punctuation.

    >>> extract_words('anything else.....not my job')
    ('anything', 'else', 'not', 'my', 'job')
    >>> extract_words('i love my job. #winning')
    ('i', 'love', 'my', 'job', 'winning')
    >>> extract_words('make justin # 1 by tweeting #vma #justinbieber :)')
    ('make', 'justin', 'by', 'tweeting', 'vma', 'justinbieber')
    >>> extract_words("paperclips! they're so awesome, cool, & useful!")
    ('paperclips', 'they', 're', 'so', 'awesome', 'cool', 'useful')
    """
    "*** YOUR CODE HERE ***"
    
    new_text = ''
    for char in text:
        if (char in string.ascii_letters) or (char == ' '):
            new_text += char
        else:
            new_text += ' '
        
    return tuple(new_text.split())


def get_word_sentiment(word):
    """Return a number between -1 and +1 representing the degree of positive or
    negative feeling in the given word. 

    Return None if the word is not in the sentiment dictionary.
    (0 represents a neutral feeling, not an unknown feeling.)
    
    >>> get_word_sentiment('good')
    0.875
    >>> get_word_sentiment('bad')
    -0.625
    >>> get_word_sentiment('winning')
    0.5
    >>> get_word_sentiment('Berkeley')  # Returns None
    """
    return get_data(word)

def analyze_tweet_sentiment(tweet):
    """ Return a number between -1 and +1 representing the degree of positive or
    negative sentiment in the given tweet, averaging over all the words in the
    tweet that have a sentiment score. 

    If there are words that don't have a sentiment score, leave them 
    out of the calculation. 

    If no words in the tweet have a sentiment score, return None.
    (do not return 0, which represents neutral sentiment).

    >>> positive = make_tweet('i love my job. #winning', None, 0, 0)
    >>> round(analyze_tweet_sentiment(positive), 5)
    0.29167
    >>> negative = make_tweet("Thinking, 'I hate my job'", None, 0, 0)
    >>> analyze_tweet_sentiment(negative)
    -0.25
    >>> no_sentiment = make_tweet("Go bears!", None, 0, 0)
    >>> analyze_tweet_sentiment(no_sentiment)
    """
    total = 0
    i = 0
    "*** YOUR CODE HERE ***"
    sentence = tweet_words(tweet)
    none_sentence = 0

    for element in sentence:
        if get_word_sentiment(element) == None:
            none_sentence += 1
        else:
            total += get_word_sentiment(element)
            i += 1
            
    if none_sentence == len(sentence):
        return None
    else:
        return total/i


def print_sentiment(text='Are you virtuous or verminous?'):
    """Print the words in text, annotated by their sentiment scores.

    For example, to print each word of a sentence with its sentiment:

    # python3 trends.py 'favorite family layman'
    """
    words = extract_words(text.lower())
    assert words, 'No words extracted from "' + text + '"'
    layout = '{0:>' + str(len(max(words, key=len))) + '}: {1}'
    for word in extract_words(text.lower()):
        print(layout.format(word, get_word_sentiment(word)))
        

# Phase 2: The geometry of maps

def find_centroid(polygon):
    """Find the centroid of a polygon.

    http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon
    
    polygon -- A tuple of positions, in which the first and last are the same

    Returns: 3 numbers; centroid latitude, centroid longitude, and polygon area

    Hint: If a polygon has 0 area, return its first position as its centroid

    >>> p1, p2, p3 = make_position(1, 2), make_position(3, 4), make_position(5, 0)
    >>> triangle = (p1, p2, p3, p1)  # First vertex is also the last vertex
    >>> find_centroid(triangle)
    (3.0, 2.0, 6.0)
    >>> find_centroid((p1, p3, p2, p1))
    (3.0, 2.0, 6.0)
    >>> find_centroid((p1, p2, p1))
    (1, 2, 0)
    """
    "*** YOUR CODE HERE ***"

    i = 0
    area_total = 0
    cenlat_total = 0
    cenlong_total = 0

    while i < len(polygon) - 1:
            area_total += (latitude(polygon[i]) * longitude(polygon[i+1])) - (latitude(polygon[i+1])*longitude(polygon[i]))
            i += 1
    area_total = area_total/2

    i = 0

    if area_total != 0:
        
        while i < len(polygon) - 1:
            cenlat_total += (latitude(polygon[i]) + latitude(polygon[i+1])) * ((latitude(polygon[i])*longitude(polygon[i+1])) - (latitude(polygon[i+1])*longitude(polygon[i])))
            cenlong_total += (longitude(polygon[i]) + longitude(polygon[i+1])) * ((latitude(polygon[i])*longitude(polygon[i+1])) - (latitude(polygon[i+1])*longitude(polygon[i])))
            i += 1
        cenlat_total = cenlat_total/(6*area_total)
        cenlong_total = cenlong_total/(6*area_total)

        
    else:
        return (latitude(polygon[0]), longitude(polygon[0]), 0)

    return (cenlat_total, cenlong_total, abs(area_total))
    
def find_center(shapes):
    """Compute the geographic center of a state, averaged over its shapes.

    The center is the average position of centroids of the polygons in shapes,
    weighted by the area of those polygons.
    
    Arguments:
    # shapes -- a list of polygons
    shapes -- a tuple of polyons

    >>> ca = find_center(idict_select(us_states, 'CA'))  # California
    >>> round(latitude(ca), 5)
    37.25389
    >>> round(longitude(ca), 5)
    -119.61439

    >>> hi = find_center(idict_select(us_states, 'HI'))  # Hawaii
    >>> round(latitude(hi), 5)
    20.1489
    >>> round(longitude(hi), 5)
    -156.21763
    """
    "*** YOUR CODE HERE ***"
    total_lat = 0
    total_long = 0
    total_area = 0
    for element in shapes:
        total_area += find_centroid(element)[2]
        total_lat += find_centroid(element)[0]* find_centroid(element)[2]
        total_long += find_centroid(element)[1]* find_centroid(element)[2]

    return (total_lat/total_area, total_long/total_area)



def draw_centered_map(center_state='TX', n=10):
    """Draw the n states closest to center_state.
    
    For example, to draw the 20 states closest to California (including California),
    enter in the terminal: 

    # python3 trends.py CA 20
    """
    us_centers = make_idict()
    for i, s in idict_items(us_states):
        us_centers = idict_insert(us_centers, i, find_center(s))
    center = idict_select(us_centers, center_state.upper())
    dist_from_center = lambda name: geo_distance(center, idict_select(us_centers, name)) 
    for name in sorted(idict_keys(us_states), key=dist_from_center)[:int(n)]:
        draw_state(idict_select(us_states, name))
        draw_name(name, idict_select(us_centers, name))
    draw_dot(center, 1, 10)  # Mark the center state with a red dot
    wait()


# Phase 3: The mood of the nation

def find_closest_state(tweet, state_centers):
    """Return the name of the state closest to the given tweet's location.
    
    Use the geo_distance function (already provided) to calculate distance 
    in miles between two latitude-longitude positions.

    Arguments:
    tweet -- a tweet abstract data type
    state_centers -- a immutable dictionary from state names to positions

    >>> us_centers = make_idict()
    >>> for n, s in idict_items(us_states):
    ...     us_centers = idict_insert(us_centers, n, find_center(s)) 
    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> find_closest_state(sf, us_centers)
    'CA'
    >>> find_closest_state(ny, us_centers)
    'NJ'
    """
    "*** YOUR CODE HERE ***"
    
    distance_tup = ()
    tweet_position = tweet_location(tweet)
    for n, s in idict_items(state_centers):
        distance_tup += geo_distance(tweet_position, idict_select(state_centers, n)),
   
    want = min(distance_tup)
    
        

    for n, s in idict_items(state_centers):
        if geo_distance(tweet_position, idict_select(state_centers, n)) == want:
            return n
            

def group_tweets_by_state(tweets):
    """Return an immutable dictionary that aggregates tweets by their nearest state center.

    The keys of the returned dictionary are state names, and the values are
    tuples of tweets that appear closer to that state center than any other.
     
    tweets -- a tuple of tweet abstract data types

    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> la = make_tweet("Welcome to Los Angeles", None, 34, -118)
    >>> ca_tweets = idict_select(group_tweets_by_state((sf, la)), 'CA')
    >>> tweet_string(ca_tweets[0])
    '"Welcome to San Francisco" @ (38, -122)'
    >>> tweet_string(ca_tweets[1])
    '"Welcome to Los Angeles" @ (34, -188)'
    """
    tweets_by_state, us_centers = make_idict(), make_idict()
    for n, s in idict_items(us_states):
        us_centers = idict_insert(us_centers, n, find_center(s)) 

    "*** YOUR CODE HERE ***"
    
    tup_states = ()
    for n, s in idict_items(us_states):
        tup_states += n,
        
    for state in tup_states:
        tup_cities = ()
        for elem in tweets:
            if find_closest_state(elem, us_centers) == state:
                tup_cities += elem,
                tweets_by_state = idict_insert(tweets_by_state, state, tup_cities)

    return tweets_by_state
    
def calculate_average_sentiments(tweets_by_state):
    """Calculate the average sentiment of the states by averaging over all 
    the tweets from each state that have a sentiment value. Return the result
    as an immutable dictionary from state names to average sentiment values.
   
    If a state has no tweets with sentiment values, leave it out of the
    dictionary entirely.  Do not include a states with no tweets, or with tweets
    that have no sentiment, as 0.  0 represents neutral sentiment, not unknown
    sentiment.

    tweets_by_state -- An immutable dictionary from state names to tuples of tweets
    """
    averaged_state_sentiments = make_idict()
    "*** YOUR CODE HERE ***"
    place_holder = 0
    for n, t in idict_items(tweets_by_state):
        i = 0
        total_sentiment = 0
        counter = 0
        while i < len(t):
            if analyze_tweet_sentiment(t[i]) == None:
                place_holder += 1
            else:
                total_sentiment += analyze_tweet_sentiment(t[i])
                counter += 1
            i += 1
        if counter != 0:
            averaged_state_sentiments = idict_insert(averaged_state_sentiments, n, total_sentiment/counter)

    
    return averaged_state_sentiments

def draw_state_sentiments(state_sentiments=make_idict()):
    """Draw all U.S. states in colors corresponding to their sentiment value.
    
    Unknown state names are ignored; states without values are colored grey.
    
    state_sentiments -- An immutable dictionary from state strings to sentiment values
    """
    for name, shapes in idict_items(us_states):
        sentiment = idict_select(state_sentiments, name)
        draw_state(shapes, sentiment)
    for name, shapes in idict_items(us_states):
        center = find_center(shapes)
        if center is not None:
            draw_name(name, center)

def draw_map_for_term(term='my job'):
    """
    Draw the sentiment map corresponding to the tweets that match term.
    
    term -- a word or phrase to filter the tweets by.  
    
    To visualize tweets containing the word "obama":
    
    # python3 trends.py obama
    
    Some term suggestions:
    New York, Texas, sandwich, my life, justinbieber
    """
    tweets = load_tweets(make_tweet, term)
    tweets_by_state = group_tweets_by_state(tweets)
    state_sentiments = calculate_average_sentiments(tweets_by_state)
    draw_state_sentiments(state_sentiments)
    for tweet in tweets:
        draw_dot(tweet_location(tweet), analyze_tweet_sentiment(tweet))
    wait()

#################################################################
##   You don't need to look at this unless you really want to  ##
#################################################################

def setup_args():
    """Reads in the command-line argument, and chooses an appropriate
    action.

    Note: this function uses Python syntax/techniques not yet covered
          in this course. You do not need to understand how this works.
    """
    import argparse

    description = """Run your project code in a specific manner. For \
instance, to run the print_sentiment code, do: 'python3 trends.py \
--print_sentiment "favorite family lowerclassman" '. Defaults to {0} if no argument is \
given.""".format('--print_sentiment')

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('fn_args', nargs='*')
    parser.add_argument('--print_sentiment', '-3', const=print_sentiment,
                        action='store_const', dest='fn',
                        help="Prints the sentiment of each word of a \
given sentence.")
    parser.add_argument('--draw_centered_map', '-6', const=draw_centered_map,
                        action='store_const', dest='fn',
                        help="Draws the N closest states to a given STATE.")
    parser.add_argument('--draw_map_for_term', '-9', const=draw_map_for_term,
                        action='store_const', dest='fn', 
                        help="Displays the sentiments for a given term.")

    args = parser.parse_args()
    if not args.fn:
        args.fn = print_sentiment
    if args.fn == print_sentiment:
        if args.fn_args:
            wds = ' '.join(args.fn_args)
            return lambda: args.fn(wds)
        else:
            return lambda: args.fn()
    elif args.fn == draw_centered_map:
        if len(args.fn_args) <= 1:
            centerstate = args.fn_args
            return lambda: args.fn(centerstate)
        else:
            centerstate, n = args.fn_args
            return lambda: args.fn(centerstate, n)
    else:
        return lambda: args.fn(args.fn_args[0])
    
@main
def run(*args):
    fn = setup_args()
    fn()
