#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import time
import logging
import operator
from beaker.cache import cache_region
from gensim.models import ldamodel
from . import corpus

log = logging.getLogger()


@cache_region('long_term')
def get_lda(c, n_topics=4):
    """
    Get LDA model
    :param n_topics: Number of topics to use in model
    :param c: Corpus object
    :return: LDA model
    """
    lda = ldamodel.LdaModel(c.corpus, id2word=c.dic, num_topics=n_topics)
    return lda


@cache_region('long_term')
def crime_topics(
        status_base,
        crimes_base,
        n_topics=4):
    """
    Generate crime topics
    :return: dict with term frequency calculated by LDA
    """
    t0 = time.clock()
    c = corpus.get_events_corpus(status_base)
    t1 = time.clock() - t0
    log.debug("TOPICS: Time to generate Corpus for topics: %s seconds", t1)

    t0 = time.clock()
    lda = get_lda(c, n_topics)
    t1 = time.clock() - t0
    log.debug("TOPICS: Time to generate LDA Model in base %s for %s topics: %s seconds",
              status_base.lbbase.metadata.name,
              n_topics,
              t1)

    topics_list = lda.show_topics(num_topics=n_topics, formatted=False)
    base_info = status_base.get_base()
    total_status = int(base_info['result_count'])

    saida = dict()
    i = 0

    # Now we allow the status to be in only one category
    # Consider the highest probability
    found_categories = list()
    for elm in topics_list:
        saida[i] = dict()
        saida[i]['tokens'] = list()
        for token in elm:
            probability = token[0]
            word = token[1]
            if total_status is not None:
                token_dict = dict(
                    word=word,
                    probability=probability,
                    frequency=probability*total_status
                )
            else:
                token_dict = dict(
                    word=word,
                    probability=probability,
                    frequency=None
                )
            saida[i]['tokens'].append(token_dict)

            # Get category if we didn't find it yet
            if saida[i].get('category') is None:
                category = crimes_base.get_token_by_name(word)
                if category is None:
                    continue
                if category['category_name'] not in found_categories:
                    found_categories.append(category['category_name'])
                    saida[i]['category'] = crimes_base.get_token_by_name(word)

                    # Finish searching
                    continue

        i += 1

    return saida


@cache_region('long_term')
def get_category(status,
                 status_base,
                 crimes_base,
                 n_topics=4):

    t0 = time.clock()
    c = corpus.get_events_corpus(status_base)
    t1 = time.clock() - t0
    log.debug("CATEGORY: Time to generate Corpus: %s seconds", t1)

    t0 = time.clock()
    lda = get_lda(c, n_topics)
    t1 = time.clock() - t0
    log.debug("CATEGORY: Time to generate LDA Model in base %s for %s topics: %s seconds",
              status_base.lbbase.metadata.name,
              n_topics,
              t1)

    # Produce sorted list of probabilities
    if status.get('events_tokens') is not None:
        vec_bow = c.dic.doc2bow(status['events_tokens'])
    else:
        # Use search term when it is not possible to use events tokens
        vec_bow = c.dic.doc2bow([status['search_term']])
    vec_lda = lda[vec_bow]
    sorted_vec_lda = sorted(vec_lda, key=operator.itemgetter(1), reverse=True)

    # Get categories
    category_list = crime_topics(
        status_base,
        crimes_base,
        n_topics
    )

    # This will the topic with highest probability
    category_index = sorted_vec_lda[0][0]
    category = category_list[category_index]

    if category.get('category') is not None:
        # Add this category back to status
        status['category'] = {
            'category_id_doc': category['category']['_metadata']['id_doc'],
            'category_probability': sorted_vec_lda[0][1]
        }
    else:
        status['category'] = {}

    return status