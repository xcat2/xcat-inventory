# -*- coding: utf-8 -*-


from flask import Blueprint

console_bp = Blueprint('ui', __name__, url_prefix='/ui')


from . import main

