from django.shortcuts import render

from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "main/index.html"


class PrivacyView(TemplateView):
    template_name = "main/privacy.html"


class TermsView(TemplateView):
    template_name = "main/terms.html"
