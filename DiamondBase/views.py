from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import os

def media_xsendfile(request,path):
    document_root = settings.MEDIA_ROOT
    response=HttpResponse()
    response['Content-Type'] = ''
    response['X-Sendfile'] = (os.path.join(document_root,path)).encode('utf-8')
    return response
