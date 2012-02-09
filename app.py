import os
import sqlalchemy
from flask import Flask, g, session, request, render_template
from flaskext.openid import OpenID

app = Flask(__name__)
oid = OpenID(app, 'openid-store')

app.secret_key = os.environ.get('SESSION_KEY', 'A552BC3A5DA23094084D53B017DED')

@app.route("/")
def hello():
    return "Hello World!"

@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=openid).first()

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
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())

if __name__ == "__main__":
    app.run(debug=True)
