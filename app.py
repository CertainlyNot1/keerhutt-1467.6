from app import create_app
from app.extensions import sockatia
app = create_app()
if __name__ == '__main__':
    sockatia.run(app,debug=True)