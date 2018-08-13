# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json

import extract


# Usage:
# curl -XPOST http://localhost:8000/ke/ -d'{ "query": [ "It was found by some of the instructors that the administration of online courses to be time consuming.", "Students were frustrated by the difficulty in contacting other lectures by email.", "Difficulty in acquiring new teaching and technological skills." ] }' > z.html


extract.initialize()


@csrf_exempt
def index(request):
    if request.method == 'GET':
        return HttpResponse("Hello, GET world.")
    elif request.method == 'POST':
        assert len(request.POST) == 1
        post_body = list(request.POST.keys())[0]
        items = json.loads(post_body)["query"]
        keyword_tokens = extract.backend(items)
        keywords = extract.tokens_to_dicts(keyword_tokens)

        extracted = {"response": keywords}
        return HttpResponse(json.dumps(extracted))
