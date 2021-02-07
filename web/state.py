from flask import Blueprint, render_template
from flask import current_app as app

from pathlib import Path
import time

import jimi

from plugins.state.models import state

pluginPages = Blueprint('statePages', __name__, template_folder="templates")

@pluginPages.route("/state/")
def mainPage():
    foundStates = state._state().query(sessionData=jimi.api.g.sessionData)["results"]
    return render_template("state.html", states=foundStates)
