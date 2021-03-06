# -*- coding: utf-8 -*-
"""
    tests.up_and_running
    ~~~~~~~~~~~~~~~~~~~~~
    Ensures the service is running and test basic functions.

    :copyright: (c) 2017 Yoan Tournade.
    :license: MIT, see LICENSE for more details.
"""
import pytest
import requests
import os
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession

SAMPLE_DIR = os.getcwd() + '/tests/samples/'

COMPIL_HELLO_WORLD = {
    'resources': [
        {
            'content': '\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}'
        }
    ]
}
PDF_HELLO_WORLD = SAMPLE_DIR + 'hello_world.pdf'

def compareToSample(r, samplePath):
    with open(PDF_HELLO_WORLD, 'rb') as f:
        sample = f.read()
        assert len(r.content) == len(sample)
        # Generated binary PDF files differs.
        # TODO Use https://github.com/euske/pdfminer to compare?
        # assert generated == sample
        # Or read as string (utf-8) and compare N first charachers.
        # We may also find at which offset(s) the content differ between
        # compilation and compare all but that.

def test_api_index_redirect(latex_on_http_api_url):
    """
    The API index currently redirect to the GitHub repository.
    """
    r = requests.get(latex_on_http_api_url, allow_redirects=False)
    assert r.status_code == 302
    assert r.headers['location'] == 'https://github.com/YtoTech/latex-on-http'

def test_simple_compilation_body(latex_on_http_api_url):
    """
    Compile a simple Latex document, text-only, passed directly in document
    definition content entry.
    """
    r = requests.post(
        latex_on_http_api_url + '/compilers/latex', json=COMPIL_HELLO_WORLD
    )
    assert r.status_code == 201
    compareToSample(r, PDF_HELLO_WORLD)

def test_concurrent_compilations(latex_on_http_api_url):
    """
    We can launch multiple compilation jobs concurrently.
    """
    concurrentSessions = 16
    session = FuturesSession(executor=ThreadPoolExecutor(max_workers=concurrentSessions))
    requestsList = []
    # Spam all requests concurrently.
    for i in range(0, concurrentSessions):
        requestsList.append(session.post(
            latex_on_http_api_url + '/compilers/latex', json=COMPIL_HELLO_WORLD
        ))
    # Check the API ping during load.
    r = requests.get(latex_on_http_api_url, allow_redirects=False, timeout=0.1)
    assert r.status_code == 302
    # Check all results.
    for requestFuture in requestsList:
        r = requestFuture.result()
        assert r.status_code == 201
        compareToSample(r, PDF_HELLO_WORLD)


# TODO API ping

# with open('hello_world.pdf', 'wb') as f:
#     f.write(r.content)
