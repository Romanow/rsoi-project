import sys
sys.path.append("..")
sys.path.append("../common")

from qrconfig import QRYamlConfig

from auth.app import create_app


app = create_app('qrook_auth', 'config.yaml')
#     {
#     'SECRET_KEY': 'secret',       # todo about this?!
#     #'SQLALCHEMY_TRACK_MODIFICATIONS': False,
#     #'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
# })


@app.cli.command()
def initdb():
    from auth.models import db
    db.create_all()


if __name__ == '__main__':
    # app = create_app({
    #     'SECRET_KEY': 'secret',
    #     # 'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    #     # 'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
    # })

    config = QRYamlConfig()
    config.read_config('config.yaml')

    #initdb()
    app.run(host=config.app.host, port=config.app.port, debug=config.app.debug)     # todo local