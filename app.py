import os
import sqlalchemy
from flask import Flask, g, session, request, render_template, flash, url_for, \
    redirect

from flaskext.openid import OpenID

app = Flask(__name__)
oid = OpenID(app, 'openid-store')

app.secret_key = os.environ.get('SESSION_KEY', 'A552BC3A5DA23094084D53B017DED')

@app.route("/")
def main_page():
    return render_template('main.html',
                           openid_url=session.get('openid'),
                           name=request.args.get('name'))

@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        # XXX do something with the database here
        g.user = session['openid']

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['email', 'fullname',
                                                  'nickname'])
    return render_template('login.html',
                           next=oid.get_next_url(),
                           error=oid.fetch_error())

@oid.after_login
def create_or_login(resp):
    session['openid'] = resp.identity_url
    flash(u'Successfully signed in as %s' % session['openid'])
    return redirect(url_for('main_page',
                            next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))

if __name__ == "__main__":
    app.run(debug=True)
